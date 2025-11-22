import json
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
            response = json.loads(connection.recv(4096))
            assert response == {
                "bots": [
                    {
                        "login": "TEST",
                        "account_id": 1,
                        "connected": False,
                        "in_fight": False,
                        "current_behavior": None,
                    }
                ]
            }

        with socket.create_connection(("127.0.0.1", 16666)) as connection:
            connection.sendall(b"TEST\n1+1\n---END---\n")
            response = json.loads(connection.recv(4096))
            assert response == {"stdout": "", "result": "2", "error": None}

        with socket.create_connection(("127.0.0.1", 16666)) as connection:
            connection.sendall(b"UNKNOWN\ncode\n---END---\n")
            response = json.loads(connection.recv(4096))
            assert response == {"stdout": "", "result": None, "error": "Unknown bot login 'UNKNOWN'"}
    finally:
        server.stop()
