import socket
import sys
from dataclasses import dataclass, field
from pathlib import Path
from socket import AF_INET6
from socket import socket as Socket
from threading import Thread

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.consts import CONNECTION_SERVERS_IPS
from src.gui.application import launch_gui
from src.gui.signals.msg_signals import MessageSignals
from src.mitm.connection_proxy import ConnectionProxy
from src.mitm.game_proxy import GameProxy
from src.mitm.proxy import Proxy


@dataclass
class ListenerManager:
    msg_signals: MessageSignals
    proxies: list[Proxy] = field(default_factory=lambda: [], init=False)

    def on_mitm_connection_callback(
        self, client_socket: Socket, server_socket: Socket
    ) -> None:
        def on_game_connection_callback(
            host_port: int, target_address: tuple[str, int]
        ) -> None:
            Thread(
                target=lambda: self.start_listener(host_port, target_address),
                daemon=True,
            ).start()

        if server_socket.getpeername()[0] in CONNECTION_SERVERS_IPS:
            bridge = ConnectionProxy(
                msg_signals=self.msg_signals,
                on_game_connection_callback=on_game_connection_callback,
                client_socket=client_socket,
                server_socket=server_socket,
            )
        else:
            bridge = GameProxy(
                msg_signals=self.msg_signals,
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
            address=("localhost", host_port),
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


def main():
    msg_signals = MessageSignals()
    listener = ListenerManager(msg_signals)
    Thread(
        target=lambda: listener.start_listener(
            5555, ("dofus2-co-beta.ankama-games.com", 5555), True
        ),
        daemon=True,
    ).start()
    launch_gui(msg_signals)


if __name__ == "__main__":
    main()
