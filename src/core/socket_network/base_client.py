import select
from dataclasses import dataclass
from socket import AF_INET, SOCK_STREAM, socket

from ankama_launcher_emulator_premium.utils.internet import has_internet_connection

from src.core.bot.bot import Bot
from src.protocol.protocol import decode_varint_size


@dataclass(kw_only=True)
class BaseClient:
    bot: Bot
    interface_ip: str | None = None

    def __post_init__(self) -> None:
        self.client_socket: socket = socket(AF_INET, SOCK_STREAM)
        self.buffer = bytes()

    def connect_socket(self, host: str, port: int) -> None:
        if self.interface_ip is not None:
            self.client_socket.bind((self.interface_ip, 0))
        self.client_socket.connect((host, port))

    def loop(self) -> None:
        active = True
        try:
            while active:
                if self.client_socket.fileno() == -1:
                    break
                rlist, wlist, xlist = select.select(
                    [self.client_socket], [], [self.client_socket]
                )
                if xlist:
                    for error in xlist:
                        self.bot.logger.error(f"error socket : {error}")
                if xlist or not rlist:
                    break
                for r in rlist:
                    data: bytes = r.recv(8192)
                    if not data:
                        active = False
                        break
                    self.handle(data)
        except (ConnectionResetError, BrokenPipeError, OSError, ValueError) as err:
            self.bot.logger.warning(f"Network error in proxy loop: {err}")
        finally:
            self.close()

    def handle(self, data: bytes) -> None:
        self.buffer += data

        while True:
            if len(self.buffer) == 0:
                break
            try:
                size, pos = decode_varint_size(self.buffer)
            except IndexError:
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

    def close(self):
        self.bot.logger.info(
            f"closing conns, internet connection is {has_internet_connection()}"
        )
        self.client_socket.close()
        self.on_close()

    def on_close(self): ...
