import socket
from dataclasses import dataclass, field
from socket import AF_INET6
from socket import socket as Socket
from threading import Thread
from time import sleep

from src.const import CONNECTION_SERVERS_IPS
from src.controller.bot_config import BotConfigController
from src.core.bot.bot import Bot
from src.core.mitm.connection_proxy import ConnectionProxy
from src.core.mitm.game_proxy import GameProxy
from src.core.mitm.proxy import Proxy
from src.utils.internet import ETHER_IP, has_internet_connection
from src.utils.pids import get_pid_by_local_and_remote_port


@dataclass
class ProxyListener:
    account_by_id: dict[int, Bot]
    account_by_port: dict[int, Bot] = field(init=False, default_factory=lambda: {})
    proxies: list[Proxy] = field(default_factory=lambda: [], init=False)
    _listener_sockets: list[Socket] = field(default_factory=list, init=False)
    _shutdown_requested: bool = field(default=False, init=False)

    def _get_bot_network_interface(self, bot: Bot | None) -> str | None:
        if bot is None:
            return None
        login = bot.account["apikey"]["login"]
        configs = BotConfigController().get_bot_config_by_login()
        config = configs.get(login)
        return config.network_interface if config else None

    def on_mitm_connection_callback(
        self, client_socket: Socket, server_socket: Socket, host_port: int
    ) -> None:
        def on_game_connection_callback(
            target_address: tuple[str, int], bot: Bot
        ) -> int:
            proxy_socket = self.create_server()
            host_port = proxy_socket.getsockname()[1]
            self.account_by_port[host_port] = bot
            Thread(
                target=lambda: self.start_listener(
                    proxy_socket, target_address, bot=bot
                ),
                daemon=True,
            ).start()
            return host_port

        bridge: Proxy
        if server_socket.getpeername()[0] in CONNECTION_SERVERS_IPS:
            local_port = client_socket.getpeername()[1]
            related_pid = get_pid_by_local_and_remote_port(
                local_port=local_port, remote_port=host_port
            )
            if related_pid is None:
                return print("Did not found related pid")

            related_bot = next(
                (
                    bot
                    for bot in self.account_by_id.values()
                    if bot.process_manager.pid == related_pid
                ),
                None,
            )
            bridge = ConnectionProxy(
                bot=related_bot,
                on_game_connection_callback=on_game_connection_callback,
                client_socket=client_socket,
                server_socket=server_socket,
                bot_by_id=self.account_by_id,
            )
        else:
            bridge = GameProxy(
                bot=self.account_by_port[client_socket.getsockname()[1]],
                client_socket=client_socket,
                server_socket=server_socket,
            )
        self.proxies.append(bridge)

        bridge.loop()

    def create_server(self, port: int = 0) -> Socket:
        return socket.create_server(
            address=("::", port),
            family=AF_INET6,
            backlog=5,
            dualstack_ipv6=True,
        )

    def start_listener(
        self,
        proxy_socket: Socket,
        target_address: tuple[str, int],
        forever: bool = False,
        bot: Bot | None = None,
    ):
        def on_connection(client_socket: Socket, host_port: int):
            print(f"received connection from {client_socket.getpeername()}")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            interface_ip = self._get_bot_network_interface(bot)
            if interface_ip:
                print(f"binding to {interface_ip}")
                server_socket.bind((interface_ip, 0))
            elif ETHER_IP:
                print(f"binding to {ETHER_IP}")
                server_socket.bind((ETHER_IP, 0))

            def connect_timeout_proof(retry: int = 5):
                try:
                    server_socket.connect(target_address)
                except (TimeoutError, socket.gaierror, OSError) as err:
                    if retry > 0:
                        while not has_internet_connection():
                            sleep(1)
                        sleep(1)
                        connect_timeout_proof(retry - 1)
                    else:
                        raise err

            connect_timeout_proof()
            print(f"connect to {server_socket.getpeername()}")
            self.on_mitm_connection_callback(client_socket, server_socket, host_port)

        host_port = proxy_socket.getsockname()[1]

        self._listener_sockets.append(proxy_socket)
        proxy_socket.settimeout(1.0)
        print(f"listening on {host_port} at localhost for target {target_address}")
        while not self._shutdown_requested:
            try:
                client_socket, _ = proxy_socket.accept()
                on_connection(client_socket, host_port)
                if not forever:
                    break
            except socket.timeout:
                continue
            except OSError:
                break

    def shutdown(self) -> None:
        self._shutdown_requested = True
        for proxy in self.proxies:
            proxy.close()
        self.proxies.clear()
        for sock in self._listener_sockets:
            try:
                sock.close()
            except OSError:
                pass
        self._listener_sockets.clear()
