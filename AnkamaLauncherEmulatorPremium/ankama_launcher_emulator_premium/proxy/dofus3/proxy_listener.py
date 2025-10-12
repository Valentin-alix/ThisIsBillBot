import logging
import socket
from dataclasses import dataclass, field
from socket import AF_INET6
from socket import socket as Socket
from threading import Lock, Thread
from time import sleep

import socks

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.proxy.dofus3.proxy import Proxy
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.proxy import get_info_by_proxy_url

logger = logging.getLogger()

DOFUS_CONNECTION_HOST = "dofus2-co-production.ankama-games.com"
DOFUS_CONNECTION_PORT = 5555


@dataclass
class ProxyListener:
    proxies: list[Proxy] = field(default_factory=lambda: [], init=False)
    _proxies_lock: Lock = field(default_factory=Lock, init=False)
    _listener_sockets: list[Socket] = field(default_factory=lambda: [], init=False)
    _shutdown_requested: bool = field(default=False, init=False)

    def create_bridge(self, client_socket: Socket, server_socket: Socket, host_port: int) -> Proxy | None:
        return Proxy(client_socket=client_socket, server_socket=server_socket)

    def start_game_listener(
        self,
        target_address: tuple[str, int],
        proxy_url: str | None = None,
    ) -> int:
        proxy_socket = self.create_server()
        game_port = proxy_socket.getsockname()[1]
        Thread(
            target=lambda: self.start_listener(
                proxy_socket,
                target_address,
                proxy_url=proxy_url,
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
        proxy_url: str | None = None,
    ) -> int:
        proxy_socket = self.create_server(port)
        bound_port = proxy_socket.getsockname()[1]
        Thread(
            target=lambda: self.start_listener(
                proxy_socket,
                target_address,
                forever=True,
                proxy_url=proxy_url,
            ),
            daemon=True,
        ).start()
        return bound_port

    def start_listener(
        self,
        proxy_socket: Socket,
        target_address: tuple[str, int],
        forever: bool = False,
        proxy_url: str | None = None,
    ) -> None:
        def on_connection(client_socket: Socket, host_port: int) -> None:
            logger.info(f"received connection from {client_socket.getpeername()}")
            server_socket = self.create_server_socket(proxy_url)

            def connect_with_retry(retry: int = 5) -> None:
                try:
                    server_socket.connect(target_address)
                except (TimeoutError, socket.gaierror, OSError) as err:
                    if retry > 0 and not self._shutdown_requested:
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
            except TimeoutError:
                continue
            except OSError:
                break

    def create_server_socket(self, proxy_url: str | None = None) -> socks.socksocket:
        server_socket = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        if proxy_url:
            parsed = get_info_by_proxy_url(proxy_url)
            server_socket.set_proxy(
                socks.SOCKS5,
                addr=parsed.hostname,
                port=parsed.port,
                username=parsed.username,
                password=parsed.password,
                rdns=False,
            )
        return server_socket

    def on_mitm_connection_callback(
        self, client_socket: Socket, server_socket: Socket, host_port: int
    ) -> None:
        bridge = self.create_bridge(client_socket, server_socket, host_port)
        if bridge is None:
            return
        with self._proxies_lock:
            self.proxies.append(bridge)
        bridge.loop()

    def create_server(self, port: int = 0) -> Socket:
        return socket.create_server(
            address=("::", port),
            family=AF_INET6,
            backlog=5,
            dualstack_ipv6=True,
        )

    def on_connection_port_assigned(self, login: str, connection_port: int) -> None: ...

    def shutdown(self) -> None:
        self._shutdown_requested = True
        with self._proxies_lock:
            proxies_to_close = list(self.proxies)
            self.proxies.clear()
        for proxy in proxies_to_close:
            proxy.close()
        for sock in self._listener_sockets:
            try:
                sock.close()
            except OSError:
                pass
        self._listener_sockets.clear()
