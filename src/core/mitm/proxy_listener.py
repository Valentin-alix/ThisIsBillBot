import socket
from dataclasses import dataclass, field
from socket import AF_INET6
from socket import socket as Socket
from threading import Thread
from time import sleep

from src.const import CONNECTION_SERVERS_IPS
from src.core.bot.bot import Bot
from src.core.mitm.connection_proxy import ConnectionProxy
from src.core.mitm.game_proxy import GameProxy
from src.core.mitm.proxy import Proxy
from src.utils.internet import has_internet_connection
from src.utils.pids import get_pid_by_local_and_remote_port


@dataclass
class ProxyListener:
    account_by_id: dict[int, Bot]
    account_by_port: dict[int, Bot] = field(init=False, default_factory=lambda: {})
    proxies: list[Proxy] = field(default_factory=lambda: [], init=False)

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
                target=lambda: self.start_listener(proxy_socket, target_address),
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
    ):
        def on_connection(client_socket: Socket, host_port: int):
            print(f"received connection from {client_socket.getpeername()}")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            def connect_timeout_proof(retry: int = 5):
                try:
                    server_socket.connect(target_address)
                except (TimeoutError, socket.gaierror, OSError):
                    if retry > 0:
                        while not has_internet_connection():
                            sleep(1)
                        sleep(1)
                        connect_timeout_proof(retry - 1)

            connect_timeout_proof()
            print(f"connect to {server_socket.getpeername()}")
            self.on_mitm_connection_callback(client_socket, server_socket, host_port)

        host_port = proxy_socket.getsockname()[1]

        while True:
            print(f"listening on {host_port} at localhost for target {target_address}")
            client_socket, _ = proxy_socket.accept()
            on_connection(client_socket, host_port)
            if not forever:
                break
