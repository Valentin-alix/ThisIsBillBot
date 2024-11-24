import logging
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from random import randint
from signal import SIGTERM
from threading import Thread
from typing import Callable

from psutil import process_iter
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from ankama_launcher_emulator.consts import (
    LAUNCHER_PORT,
)
from ankama_launcher_emulator.installation.dofus3 import check_dofus3_installation
from ankama_launcher_emulator.installation.retro import check_retro_installation
from ankama_launcher_emulator.proxy.dofus3.proxy_listener import (
    BaseProxyListener,
)
from ankama_launcher_emulator.proxy.retro.retro_proxy import RetroServer
from ankama_launcher_emulator.proxy.retro.retro_text_socket_server import (
    RetroTextSocketServer,
)
from ankama_launcher_emulator.server.dofus3.launch import launch_dofus_exe
from ankama_launcher_emulator.server.retro.launch import launch_retro_exe
from ankama_launcher_emulator.utils.proxy import get_info_by_proxy_url

sys.path.append(str(Path(__file__).parent.parent.parent))

from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.gen_zaap.zaap import ZaapService
from ankama_launcher_emulator.haapi.haapi import Haapi
from ankama_launcher_emulator.interfaces.account_game_info import (
    AccountGameInfo,
)
from ankama_launcher_emulator.server.handler import (
    AnkamaLauncherHandler,
)

logger = logging.getLogger()


@dataclass
class AnkamaLauncherServer:
    handler: AnkamaLauncherHandler
    instance_id: int = field(init=False, default=0)
    _server_thread: Thread | None = None
    _dofus_threads: list[Thread] = field(init=False, default_factory=list)

    def start(self):
        for proc in process_iter():
            if proc.pid == 0:
                continue
            for conns in proc.net_connections(kind="inet"):
                if conns.laddr.port == LAUNCHER_PORT:
                    proc.send_signal(SIGTERM)

        processor = ZaapService.Processor(self.handler)
        transport = TSocket.TServerSocket(host="0.0.0.0", port=LAUNCHER_PORT)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
        Thread(target=server.serve, daemon=True).start()
        logger.info(f"Thrift server listening on port {LAUNCHER_PORT}")

        text_socket_server = RetroTextSocketServer(self.handler)
        text_socket_server.start()

    def launch_dofus(
        self,
        login: str,
        proxy_listener: BaseProxyListener,
        proxy_url: str | None = None,
        interface_ip: str | None = None,
        on_progress: Callable[[str], None] | None = None,
    ) -> int:
        logger.info(f"Launching {login} on dofus 3")

        check_dofus3_installation(on_progress)

        random_hash = str(uuid.uuid4())
        self.instance_id += 1

        api_key = CryptoHelper.getStoredApiKey(login)["apikey"]["key"]

        self.handler.infos_by_hash[random_hash] = AccountGameInfo(
            login=login,
            game_id=102,
            api_key=api_key,
            haapi=Haapi(
                api_key, interface_ip=interface_ip, login=login, proxy_url=proxy_url
            ),
        )

        connection_port = proxy_listener.start(port=0, interface_ip=interface_ip)

        return launch_dofus_exe(
            self.instance_id,
            random_hash,
            connection_port=connection_port,
            interface_ip=interface_ip,
        )

    def launch_retro(
        self,
        login: str,
        proxy_url: str | None = None,
        interface_ip: str | None = None,
        on_progress: Callable[[str], None] | None = None,
    ) -> int:
        logger.info(f"Launching {login} on retro")

        check_retro_installation(on_progress)

        logger.info("Completed retro installation")

        port = randint(57000, 63000)

        if proxy_url:
            parsed = get_info_by_proxy_url(proxy_url)
            retro_server = RetroServer(
                self.handler,
                port,
                interface_ip,
                parsed.hostname,
                parsed.port,
                parsed.username,
                parsed.password,
            )
        else:
            retro_server = RetroServer(self.handler, port, interface_ip)

        retro_server.start()

        random_hash = str(uuid.uuid4())
        self.instance_id += 1

        api_key = CryptoHelper.getStoredApiKey(login)["apikey"]["key"]

        self.handler.infos_by_hash[random_hash] = AccountGameInfo(
            login=login,
            game_id=101,
            api_key=api_key,
            haapi=Haapi(
                api_key, interface_ip=interface_ip, login=login, proxy_url=proxy_url
            ),
        )

        return launch_retro_exe(
            self.instance_id, random_hash, port, interface_ip=interface_ip
        )
