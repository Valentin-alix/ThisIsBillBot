import select
from _thread import LockType
from dataclasses import dataclass, field
from socket import AF_INET, SOCK_STREAM, socket
from threading import Lock

import socks
from ankama_launcher_emulator.utils.proxy import get_info_by_proxy_url

from src.core.bot.bot import Bot
from src.protocol.protocol import decode_varint_size


@dataclass(kw_only=True)
class BaseClient:
    bot: Bot
    proxy_url: str | None
    _close_lock: LockType = field(init=False, default_factory=Lock)
    _is_closed: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        client_socket: socket
        if self.proxy_url is None:
            client_socket = socket(AF_INET, SOCK_STREAM)
        else:
            parsed_proxy = get_info_by_proxy_url(self.proxy_url)
            socks_client_socket = socks.socksocket(AF_INET, SOCK_STREAM)
            socks_client_socket.set_proxy(
                socks.SOCKS5,
                addr=parsed_proxy.hostname,
                port=parsed_proxy.port,
                rdns=False,
                username=parsed_proxy.username,
                password=parsed_proxy.password,
            )
            client_socket = socks_client_socket
        self.client_socket = client_socket
        self.buffer = b""

    @property
    def client_label(self) -> str:
        return type(self).__name__

    def connect_socket(self, host: str, port: int) -> None:
        self.bot.logger.info(f"[{self.client_label}] Connecting to {host}:{port}, proxy={self.proxy_url}")
        self.client_socket.connect((host, port))
        self.bot.logger.info(f"[{self.client_label}] Socket connected to {host}:{port}")

    def loop(self) -> None:
        active = True
        stop_reason = "loop exited"
        try:
            while active:
                if self.client_socket.fileno() == -1:
                    stop_reason = "socket fileno is closed"
                    break
                (readable_sockets, _, exceptional_sockets) = select.select(
                    [self.client_socket], [], [self.client_socket]
                )
                if exceptional_sockets:
                    stop_reason = "socket reported exceptional state"
                    for socket_error in exceptional_sockets:
                        self.bot.logger.error(f"[{self.client_label}] error socket: {socket_error}")
                if exceptional_sockets or not readable_sockets:
                    if not readable_sockets:
                        stop_reason = "select returned no readable socket"
                    break
                for readable_socket in readable_sockets:
                    data: bytes = readable_socket.recv(8192)
                    if not data:
                        stop_reason = "remote socket closed"
                        active = False
                        break
                    self.handle(data)
        except (ConnectionResetError, BrokenPipeError, OSError, ValueError) as err:
            if self._is_closed:
                stop_reason = f"socket closed during shutdown: {type(err).__name__}: {err}"
                self.bot.logger.debug(f"[{self.client_label}] {stop_reason}")
            else:
                stop_reason = f"network error: {type(err).__name__}: {err}"
                self.bot.logger.warning(f"[{self.client_label}] Network error in socket loop: {err}")
        finally:
            self.bot.logger.info(f"[{self.client_label}] Socket loop stopping: {stop_reason}")
            self.close()

    def handle(self, data: bytes) -> None:
        self.buffer += data

        while True:
            if len(self.buffer) == 0:
                break
            try:
                size, pos = decode_varint_size(self.buffer)
            except ValueError:
                break
            if size == 0 or len(self.buffer) < pos + size:
                break

            msg_datas = self.buffer[: pos + size]
            self.buffer = self.buffer[pos + size :]

            self.on_received_msg_datas(msg_datas)

    def send(self, data: bytes) -> None:
        try:
            self.client_socket.sendall(data)
        except OSError as err:
            self.bot.logger.error(f"send to server err : {err}")
            self.close()

    def on_received_msg_datas(self, msg_datas: bytes) -> None: ...

    def close(self) -> None:
        with self._close_lock:
            if self._is_closed:
                self.bot.logger.debug(f"[{self.client_label}] connection already closed")
                return
            self._is_closed = True
            self.bot.logger.info(f"[{self.client_label}] closing conns, proxy {self.proxy_url}")
            self.client_socket.close()
        self.on_close()

    def on_close(self): ...
