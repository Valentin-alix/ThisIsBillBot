import select
from socket import socket as Socket

from src.consts import CONNECTIONS_IP
from src.protocol import decode_varint_size
from com.ankama.dofus.server.connection.protocol_pb2 import Message as ConnectionMessage


class BridgeHandler:
    def __init__(self, connection_client: Socket, connection_server: Socket):
        self.connection_client = connection_client
        self.connection_server = connection_server
        self.opposite_connection = {
            connection_client: connection_server,
            connection_server: connection_client,
        }
        self.connections = [connection_client, connection_server]
        self.buffers: dict[Socket, bytes] = {
            self.connection_client: bytes(),
            self.connection_server: bytes(),
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
            print(size, pos)
            if size == 0 or len(self.buffers[origin]) < pos + size:
                break
            content_datas = self.buffers[origin][pos : pos + size]
            if origin.getpeername()[0] in CONNECTIONS_IP:
                msg = ConnectionMessage()
                msg.ParseFromString(content_datas)
                print(msg)

            self.buffers[origin] = self.buffers[origin][pos + size :]

        self.opposite_connection[origin].sendall(data)

    def send_to_client(self, data: bytes):
        self.connection_client.sendall(data)

    def send_to_server(self, data: bytes):
        self.connection_server.sendall(data)
