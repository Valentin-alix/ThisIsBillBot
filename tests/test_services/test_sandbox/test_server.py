import socket
import time

from src.core.bot.bot import Bot
from src.services.sandbox.server import SandboxServer


def test_sandbox_server_smoke(runtime_bot: Bot) -> None:
    server = SandboxServer({1: runtime_bot}, 16666)
    server.start()
    time.sleep(0.2)
    try:
        with socket.create_connection(("127.0.0.1", 16666)) as connection:
            connection.sendall(b"list\n")
            response = connection.recv(4096)
            assert response == b"TEST\n"

        with socket.create_connection(("127.0.0.1", 16666)) as connection:
            connection.sendall(b"TEST\n1+1\n---END---\n")
            response = connection.recv(4096)
            assert response == b"STDOUT:\n\nRESULT:\n2\n"

        with socket.create_connection(("127.0.0.1", 16666)) as connection:
            connection.sendall(b"UNKNOWN\ncode\n---END---\n")
            response = connection.recv(4096)
            assert response == b"ERROR:\nUnknown bot login 'UNKNOWN'\n"
    finally:
        server.stop()
