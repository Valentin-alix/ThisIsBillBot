import logging
import socket
from dataclasses import dataclass
from threading import Thread

from ankama_launcher_emulator.consts import RETRO_TEXT_SOCKET_PORT
from ankama_launcher_emulator.server.handler import AnkamaLauncherHandler

logger = logging.getLogger()


@dataclass(eq=False)
class RetroTextSocketServer(Thread):
    """
    Mirrors the real launcher's TextSocketServer
    """

    handler: AnkamaLauncherHandler

    def __post_init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", RETRO_TEXT_SOCKET_PORT))
        self.sock.listen(5)

    def run(self):
        logger.info(f"[RETRO TEXT] Listening on port {RETRO_TEXT_SOCKET_PORT}")
        while True:
            conn, _ = self.sock.accept()
            Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn: socket.socket):
        conn.sendall(b"connected\x00")
        client_hash: str | None = None
        buf = ""
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                buf += data.decode("utf-8", errors="ignore")
                while "\x00" in buf:
                    msg, buf = buf.split("\x00", 1)
                    msg = msg.strip()
                    if msg:
                        client_hash = self._handle_command(conn, msg, client_hash)
        finally:
            conn.close()

    def _handle_command(
        self, conn: socket.socket, msg: str, client_hash: str | None
    ) -> str | None:
        parts = msg.split(" ")
        command = parts[0]
        logger.info(f"[RETRO TEXT] command: {msg}")

        if command == "connect":
            # "connect retro main <hash>"
            client_hash = parts[-1]
            conn.sendall(f"connect {client_hash}\x00".encode())

        elif command == "auth_getGameToken":
            assert client_hash
            token = self.handler.auth_getGameToken(client_hash, 101)
            conn.sendall(f"auth_getGameToken {token}\x00".encode())

        elif command == "settings_get":
            assert client_hash
            if len(parts) >= 3:
                key = parts[2]
                value = self.handler.settings_get(client_hash, key)
                conn.sendall(f"settings_get {value}\x00".encode())

        elif command == "userInfo_get":
            assert client_hash
            info = self.handler.userInfo_get(client_hash)
            conn.sendall(f"userInfo_get {info}\x00".encode())

        elif command == "zaapMustUpdate_get":
            assert client_hash
            result = self.handler.zaapMustUpdate_get(client_hash)
            conn.sendall(f"zaapMustUpdate_get {str(result).lower()}\x00".encode())

        elif command == "updater_isUpdateAvailable":
            assert client_hash
            result = self.handler.updater_isUpdateAvailable(client_hash)
            conn.sendall(
                f"updater_isUpdateAvailable {str(result).lower()}\x00".encode()
            )
        else:
            logger.warning(f"[RETRO TEXT] Unknown command: {command!r}")

        return client_hash
