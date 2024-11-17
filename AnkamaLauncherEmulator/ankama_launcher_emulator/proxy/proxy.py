import logging
import select
import socket
from dataclasses import dataclass, field
from enum import Enum, auto
from queue import Queue
from socket import socket as Socket
from threading import Lock, Thread

from google.protobuf.internal.decoder import _DecodeVarint  # type: ignore

from ankama_launcher_emulator.internet_utils import (
    has_internet_connection,  # type: ignore
)

logger = logging.getLogger()


def decode_varint_size(data: bytes) -> tuple[int, int]:
    size, new_pos = _DecodeVarint(data, 0)
    return size, new_pos


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
        self.connections: list[socket.socket] = [self.client_socket, self.server_socket]

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
                        logger.error(f"error socket : {error}")
                if xlist or not rlist:
                    break
                for r in rlist:
                    data: bytes = r.recv(8192)
                    if not data:
                        active = False
                        break
                    self.handle(data, origin=r)
        except (ConnectionResetError, BrokenPipeError, OSError, ValueError) as err:
            logger.warning(f"Network error in proxy loop: {err}")
        finally:
            self.close()

    def close(self):
        logger.info(
            f"closing conns, internet connection is {has_internet_connection()}"
        )
        for con in self.connections:
            con.close()
        with self.queue_worker_item.mutex:
            self.queue_worker_item.queue.clear()
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

            msg_datas_altered = self.alter_msg_datas(msg_content_datas, msg_datas)

            self.buffers[origin] = self.buffers[origin][pos + size :]

            if msg_datas_altered is not None:
                with self.locks[self.opposite_connection[origin]]:
                    try:
                        self.opposite_connection[origin].sendall(msg_datas_altered)
                    except OSError as err:
                        logger.error(f"sendall failed in handle: {err}")
                        return self.close()

                self.queue_worker_item.put(
                    (WorkerAction.RECEIVED, msg_datas_altered, False, from_server)
                )

    def alter_msg_datas(
        self, msg_content_datas: bytes, msg_datas: bytes
    ) -> bytes | None:
        return msg_datas

    def on_sent_msg_datas(
        self, msg_datas: bytes, was_send_from_proxy: bool, from_server: bool
    ) -> None: ...

    def send_to_client(self, data: bytes):
        with self.locks[self.client_socket]:
            try:
                self.client_socket.sendall(data)
            except OSError as err:
                logger.error(f"send to client err : {err}")
                return self.close()
        self.queue_worker_item.put((WorkerAction.RECEIVED, data, True, True))

    def send_to_server(self, data: bytes):
        with self.locks[self.server_socket]:
            try:
                self.server_socket.sendall(data)
            except OSError as err:
                logger.error(f"send to server err : {err}")
                return self.close()
        self.queue_worker_item.put((WorkerAction.RECEIVED, data, True, False))
