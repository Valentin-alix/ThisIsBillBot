import socket
from dataclasses import dataclass, field
from socket import AF_INET6
from socket import socket as Socket
from threading import Thread

from src.bot import Bot
from src.consts import CONNECTION_SERVERS_IPS
from src.mitm.connection_proxy import ConnectionProxy
from src.mitm.game_proxy import GameProxy
from src.mitm.proxy import Proxy


@dataclass
class ProxyListener:
    account_by_id: dict[int, Bot]
    account_by_port: dict[int, Bot] = field(init=False, default_factory=lambda: {})
    proxies: list[Proxy] = field(default_factory=lambda: [], init=False)

    def on_mitm_connection_callback(
        self, client_socket: Socket, server_socket: Socket
    ) -> None:
        def on_game_connection_callback(
            host_port: int, target_address: tuple[str, int], account: Bot
        ) -> None:
            self.account_by_port[host_port] = account
            Thread(
                target=lambda: self.start_listener(host_port, target_address),
                daemon=True,
            ).start()

        bridge: Proxy
        if server_socket.getpeername()[0] in CONNECTION_SERVERS_IPS:
            bridge = ConnectionProxy(
                bot_infos=self.account_by_id,
                on_game_connection_callback=on_game_connection_callback,
                client_socket=client_socket,
                server_socket=server_socket,
            )
        else:
            bridge = GameProxy(
                bot=self.account_by_port[client_socket.getsockname()[1]],
                client_socket=client_socket,
                server_socket=server_socket,
            )

        self.proxies.append(bridge)

        bridge.loop()

    def start_listener(
        self, host_port: int, target_address: tuple[str, int], forever: bool = False
    ):
        def on_connection(client_socket: Socket):
            print(f"received connection from {client_socket.getpeername()}")
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect(target_address)
            print(f"connect to {server_socket.getpeername()}")
            self.on_mitm_connection_callback(client_socket, server_socket)

        proxy_socket = socket.create_server(
            address=("::", host_port),
            family=AF_INET6,
            backlog=5,
            dualstack_ipv6=True,
        )

        while True:
            print(f"listening on {host_port} at localhost for target {target_address}")
            client_socket, _ = proxy_socket.accept()
            on_connection(client_socket)
            if not forever:
                break
