import asyncio
import socket
from socket import socket as Socket
from typing import Callable


async def start_proxy_server(
    on_mitm_connection: Callable, host_port: int, target_address: tuple[str, int]
):
    async def on_connection(client_socket: Socket):
        print(f"received connection from {client_socket.getpeername()}")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(target_address)
        print(f"connect to {server_socket.getpeername()}")
        await on_mitm_connection(client_socket, server_socket)

    proxy_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    proxy_socket.bind(("localhost", host_port))
    proxy_socket.listen(5)
    proxy_socket.setblocking(False)

    while True:
        loop = asyncio.get_running_loop()
        client_socket, _ = await loop.sock_accept(proxy_socket)
        await on_connection(client_socket)
