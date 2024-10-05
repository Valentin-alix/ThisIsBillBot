from dataclasses import dataclass, field
from socket import socket as Socket
from threading import Lock

import select
from blinker import Signal

from src.protocol.protocol import decode_varint_size


@dataclass
class Proxy:
    client_socket: Socket
    server_socket: Socket
    closed_signal: Signal = field(init=False, default_factory=lambda: Signal())
    _send_lock: Lock = field(init=False, default_factory=Lock)

    def __post_init__(self) -> None:
        self.opposite_connection = {
            self.client_socket: self.server_socket,
            self.server_socket: self.client_socket,
        }
        self.connections = [self.client_socket, self.server_socket]
        self.buffers: dict[Socket, bytes] = {
            self.client_socket: bytes(),
            self.server_socket: bytes(),
        }

    def loop(self):
        conns = self.connections
        active = True
        try:
            while active:
                rlist, wlist, xlist = select.select(conns, [], conns)
                if xlist or not rlist:
                    break
                for r in rlist:
                    data = r.recv(8192)
                    if not data:
                        active = False
                        break
                    self.handle(data, origin=r)
        finally:
            for con in conns:
                print(f"closing {con.getpeername()}")
                con.close()
            self.closed_signal.send()

    def handle(self, data: bytes, origin: Socket):
        self.buffers[origin] += data

        while True:
            if len(self.buffers[origin]) == 0:
                break
            size, pos = decode_varint_size(self.buffers[origin])
            if size == 0 or len(self.buffers[origin]) < pos + size:
                break

            msg_datas = self.buffers[origin][: pos + size]
            msg_content_datas = self.buffers[origin][pos: pos + size]

            msg_datas = self.alter_msg_datas(msg_content_datas, msg_datas)

            self.buffers[origin] = self.buffers[origin][pos + size:]

            # send msg_datas to origin target
            with self._send_lock:
                self.opposite_connection[origin].sendall(msg_datas)

            self.on_sent_msg_datas(msg_datas)

    def alter_msg_datas(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        return msg_datas

    def on_sent_msg_datas(self, msg_datas: bytes) -> None:
        ...

    def send_to_client(self, data: bytes):
        with self._send_lock:
            self.client_socket.sendall(data)
        self.on_sent_msg_datas(data)

    def send_to_server(self, data: bytes):
        with self._send_lock:
            self.server_socket.sendall(data)
        self.on_sent_msg_datas(data)
