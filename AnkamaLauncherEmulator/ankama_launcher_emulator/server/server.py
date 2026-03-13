import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Thread

from psutil import AccessDenied, NoSuchProcess, process_iter
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from ankama_launcher_emulator.consts import LAUNCHER_PORT
from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.gen_zaap.zaap import ZaapService
from ankama_launcher_emulator.haapi.haapi import Haapi
from ankama_launcher_emulator.installation.dofus3 import (
    check_dofus3_installation,
)
from ankama_launcher_emulator.interfaces.account_session import (
    AccountGameInfo,
)
from ankama_launcher_emulator.proxy.dofus3.proxy_listener import (
    ProxyListener,
)
from ankama_launcher_emulator.server.dofus3.launch import launch_dofus_exe
from ankama_launcher_emulator.server.handler import (
    AnkamaLauncherHandler,
)

logger = logging.getLogger()


@dataclass
class AnkamaLauncherServer:
    handler: AnkamaLauncherHandler
    instance_id: int = field(init=False, default=0)
    _server_thread: Thread | None = None
    _dofus_threads: list[Thread] = field(init=False, default_factory=lambda: [])

    def start(self) -> None:
        for proc in process_iter():
            if proc.pid == 0:
                continue
            try:
                connections = proc.net_connections(kind="inet")
            except (AccessDenied, NoSuchProcess):
                continue
            for connection in connections:
                if connection.laddr.port == LAUNCHER_PORT:
                    try:
                        proc.terminate()
                    except (AccessDenied, NoSuchProcess):
                        pass

        processor = ZaapService.Processor(self.handler)
        transport = TSocket.TServerSocket(host="0.0.0.0", port=LAUNCHER_PORT)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
        Thread(target=server.serve, daemon=True).start()
        logger.info(f"Thrift server listening on port {LAUNCHER_PORT}")

    def launch_dofus(
        self,
        login: str,
        proxy_listener: ProxyListener,
        proxy_url: str | None = None,
        on_progress: Callable[[str], None] | None = None,
    ) -> int:
        logger.info(f"Launching {login} on dofus 3")

        check_dofus3_installation(on_progress)

        random_hash = str(uuid.uuid4())
        self.instance_id += 1

        api_key = CryptoHelper.getStoredApiKey(login).apikey.key

        self.handler.infos_by_hash[random_hash] = AccountGameInfo(
            login=login,
            game_id=102,
            api_key=api_key,
            haapi=Haapi(api_key=api_key, login=login, proxy_url=proxy_url),
        )

        connection_port = proxy_listener.start(port=0, proxy_url=proxy_url)
        proxy_listener.on_connection_port_assigned(login, connection_port)

        return launch_dofus_exe(
            self.instance_id,
            random_hash,
            connection_port=connection_port,
        )
