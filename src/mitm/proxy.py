import select
from dataclasses import dataclass
from socket import socket as Socket

from src.protocol import decode_varint_size


@dataclass
class Proxy:
    client_socket: Socket
    server_socket: Socket

    def __post_init__(self):
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

    def handle(self, data: bytes, origin: Socket):
        self.buffers[origin] += data

        while True:
            if len(self.buffers[origin]) == 0:
                break
            size, pos = decode_varint_size(self.buffers[origin])
            if size == 0 or len(self.buffers[origin]) < pos + size:
                break

            msg_datas = self.buffers[origin][: pos + size]
            msg_content_datas = self.buffers[origin][pos : pos + size]

            msg_datas = self.handle_msg(msg_content_datas, msg_datas)

            self.buffers[origin] = self.buffers[origin][pos + size :]

            # send msg_datas to origin target
            self.opposite_connection[origin].sendall(msg_datas)

    def handle_msg(self, msg_content_datas: bytes, msg_datas: bytes) -> bytes:
        return msg_datas

    def send_to_client(self, data: bytes):
        self.client_socket.sendall(data)

    def send_to_server(self, data: bytes):
        self.server_socket.sendall(data)
