from dataclasses import dataclass, field
from enum import Enum, auto
from queue import Queue
from socket import socket as Socket
from threading import Lock, Thread

import select

from d3_mapping.protocol.protocol import decode_varint_size


class WorkerAction(Enum):
    RECEIVED = auto()
    SEND_SERVER = auto()
    SEND_CLIENT = auto()


@dataclass
class Proxy:
    client_socket: Socket
    server_socket: Socket
    queue_worker_item: Queue[tuple[WorkerAction, bytes, bool, bool]] = field(
        init=False, default_factory=Queue
    )

    def on_close(self) -> None: ...

    def __post_init__(self) -> None:
        self.opposite_connection = {
            self.client_socket: self.server_socket,
            self.server_socket: self.client_socket,
        }
        self.connections = [self.client_socket, self.server_socket]

        self.locks: dict[Socket, Lock] = {sock: Lock() for sock in self.connections}
        self.buffers: dict[Socket, bytes] = {sock: bytes() for sock in self.connections}

        self.worker_thread = Thread(target=self.run_worker, daemon=True)
        self.worker_thread.start()

    def run_worker(self):
        while True:
            action, data, was_send_from_proxy, from_server = (
                self.queue_worker_item.get()
            )
            match action:
                case WorkerAction.RECEIVED:
                    self.on_sent_msg_datas(data, was_send_from_proxy, from_server)
                case WorkerAction.SEND_CLIENT:
                    self.send_to_client(data)
                case WorkerAction.SEND_SERVER:
                    self.send_to_server(data)

    def loop(self) -> None:
        conns = self.connections
        active = True
        try:
            while active:
                rlist, wlist, xlist = select.select(conns, [], conns)
                if xlist:
                    for error in xlist:
                        print(f"error socket : {error}")
                if xlist or not rlist:
                    break
                for r in rlist:
                    data: bytes = r.recv(8192)
                    if not data:
                        active = False
                        break
                    self.handle(data, origin=r)
        except ConnectionResetError as err:
            print(err)
        finally:
            self.close()

    def close(self):
        for con in self.connections:
            print(f"closing {con.getpeername()}")
            con.close()
        self.on_close()

    def handle(self, data: bytes, origin: Socket) -> None:
        self.buffers[origin] += data

        from_server = origin == self.server_socket

        while True:
            if len(self.buffers[origin]) == 0:
                break
            try:
                size, pos = decode_varint_size(self.buffers[origin])
            except IndexError:
                break
            if size == 0 or len(self.buffers[origin]) < pos + size:
                break

            msg_datas = self.buffers[origin][: pos + size]
            msg_content_datas = self.buffers[origin][pos : pos + size]

            msg_datas_altered = self.alter_msg_datas(
                msg_content_datas, msg_datas, from_server
            )

            self.buffers[origin] = self.buffers[origin][pos + size :]

            if msg_datas_altered is not None:
                # send msg_datas to origin target
                with self.locks[self.opposite_connection[origin]]:
                    self.opposite_connection[origin].sendall(msg_datas_altered)

                self.queue_worker_item.put(
                    (WorkerAction.RECEIVED, msg_datas_altered, False, from_server)
                )

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes, from_server: bool
    ) -> bytes | None:
        return msg_datas

    def on_sent_msg_datas(
        self, msg_datas: bytes, was_send_from_proxy: bool, from_server: bool
    ) -> None: ...

    def send_to_client(self, data: bytes):
        with self.locks[self.client_socket]:
            self.client_socket.sendall(data)
        self.queue_worker_item.put((WorkerAction.RECEIVED, data, True, True))

    def send_to_server(self, data: bytes):
        with self.locks[self.server_socket]:
            self.server_socket.sendall(data)
        self.queue_worker_item.put((WorkerAction.RECEIVED, data, True, False))
