import logging
import socket
from dataclasses import dataclass, field
from socket import AF_INET6
from socket import socket as Socket
from threading import Thread
from time import sleep

import socks

from ankama_launcher_emulator.proxy.connection_proxy import (
    ConnectionProxy,
)
from ankama_launcher_emulator.proxy.proxy import Proxy

logger = logging.getLogger()

DOFUS_CONNECTION_HOST = "dofus2-co-production.ankama-games.com"
DOFUS_CONNECTION_PORT = 5555


@dataclass
class ProxyListener:
    socks5_host: str | None = None
    socks5_port: int | None = None
    socks5_username: str | None = None
    socks5_password: str | None = None

    proxies: list[Proxy] = field(default_factory=list, init=False)
    _listener_sockets: list[Socket] = field(default_factory=list, init=False)
    _shutdown_requested: bool = field(default=False, init=False)
    _initial_port: int | None = field(default=None, init=False)

    def create_bridge(
        self, client_socket: Socket, server_socket: Socket, host_port: int
    ) -> Proxy | None:
        if host_port == self._initial_port:
            return ConnectionProxy(
                on_game_connection_callback=lambda target_address: self.start_game_listener(
                    target_address
                ),
                client_socket=client_socket,
                server_socket=server_socket,
            )
        return Proxy(client_socket=client_socket, server_socket=server_socket)

    def start_game_listener(
        self, target_address: tuple[str, int], interface_ip: str | None = None
    ) -> int:
        proxy_socket = self.create_server()
        game_port = proxy_socket.getsockname()[1]
        Thread(
            target=lambda: self.start_listener(
                proxy_socket, target_address, interface_ip=interface_ip
            ),
            daemon=True,
        ).start()
        return game_port

    def start(
        self,
        port: int = DOFUS_CONNECTION_PORT,
        target_address: tuple[str, int] = (
            DOFUS_CONNECTION_HOST,
            DOFUS_CONNECTION_PORT,
        ),
        interface_ip: str | None = None,
    ) -> int:
        proxy_socket = self.create_server(port)
        bound_port = proxy_socket.getsockname()[1]
        self._initial_port = bound_port
        Thread(
            target=lambda: self.start_listener(
                proxy_socket, target_address, forever=True, interface_ip=interface_ip
            ),
            daemon=True,
        ).start()
        return bound_port

    def start_listener(
        self,
        proxy_socket: Socket,
        target_address: tuple[str, int],
        forever: bool = False,
        interface_ip: str | None = None,
    ):
        def on_connection(client_socket: Socket, host_port: int):
            logger.info(f"received connection from {client_socket.getpeername()}")
            server_socket = self.create_server_socket()
            if interface_ip:
                logger.info(f"binding to {interface_ip}")
                server_socket.bind((interface_ip, 0))

            def connect_with_retry(retry: int = 5):
                try:
                    server_socket.connect(target_address)
                except (TimeoutError, socket.gaierror, OSError) as err:
                    if retry > 0:
                        sleep(1)
                        connect_with_retry(retry - 1)
                    else:
                        raise err

            connect_with_retry()
            logger.info(f"connected to {server_socket.getpeername()}")
            self.on_mitm_connection_callback(client_socket, server_socket, host_port)

        host_port = proxy_socket.getsockname()[1]
        self._listener_sockets.append(proxy_socket)
        proxy_socket.settimeout(1.0)
        logger.info(f"listening on {host_port} for target {target_address}")

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

    def create_server_socket(self) -> socks.socksocket:
        server_socket = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        if self.socks5_host and self.socks5_port:
            server_socket.set_proxy(
                socks.SOCKS5,
                addr=self.socks5_host,
                port=self.socks5_port,
                username=self.socks5_username,
                password=self.socks5_password,
                rdns=False,
            )
        return server_socket

    def on_mitm_connection_callback(
        self, client_socket: Socket, server_socket: Socket, host_port: int
    ) -> None:
        bridge = self.create_bridge(client_socket, server_socket, host_port)
        if bridge is None:
            return
        self.proxies.append(bridge)
        bridge.loop()

    def create_server(self, port: int = 0) -> Socket:
        return socket.create_server(
            address=("::", port),
            family=AF_INET6,
            backlog=5,
            dualstack_ipv6=True,
        )

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
