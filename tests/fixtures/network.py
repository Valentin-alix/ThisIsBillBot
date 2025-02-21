from socket import socket as Socket
from unittest.mock import MagicMock


def make_socket_pair(server_ip: str) -> tuple[MagicMock, MagicMock]:
    server_socket = MagicMock(spec=Socket)
    server_socket.getpeername.return_value = (server_ip, 5555)

    client_socket = MagicMock(spec=Socket)
    client_socket.getpeername.return_value = ("10.0.0.1", 12345)

    return client_socket, server_socket
