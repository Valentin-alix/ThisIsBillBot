import logging
import socket
from dataclasses import dataclass
from threading import Thread

import socks

from ankama_launcher_emulator.server.handler import AnkamaLauncherHandler

logger = logging.getLogger()


@dataclass(eq=False)
class RetroServer(Thread):
    handler: AnkamaLauncherHandler
    port: int
    interface_ip: str | None
    socks5_host: str | None = None
    socks5_port: int | None = None
    socks5_username: str | None = None
    socks5_password: str | None = None

    def __post_init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.interface_ip or "127.0.0.1", self.port))
        self.sock.listen(1)

    def run(self):
        logger.info(f"[RETRO] Listening on port {self.port}")
        while True:
            conn, addr = self.sock.accept()
            Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn: socket.socket):
        client_hash: str | None = None
        tunneling = False
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                decoded = data.decode("utf-8", errors="ignore")
                decoded_clean = decoded.rstrip("\x00")
                logger.info(f"[RETRO] Data: {decoded_clean}")

                if decoded_clean.startswith("CONNECT "):
                    tunneling = True
                    self._start_tunnel(conn, decoded_clean)
                    return

                elif decoded_clean.startswith("connect retro main"):
                    parts = decoded_clean.split(" ")
                    if len(parts) > 0:
                        client_hash = parts[-1]
                        logger.info(
                            f"[RETRO] Connection request for UUID: {client_hash}"
                        )
                        conn.sendall(b"connected\x00")
                        conn.sendall(f"connect {client_hash}\x00".encode("utf-8"))

                elif decoded_clean.startswith("auth_getGameToken"):
                    if client_hash:
                        logger.info(f"[RETRO] Generating token for {client_hash}")
                        token_json = self.handler.auth_getGameToken(client_hash, 101)
                        token = token_json
                        response = f"auth_getGameToken {token}\x00"
                        conn.sendall(response.encode("utf-8"))
                    else:
                        logger.info(
                            "[RETRO] Error: auth_getGameToken received without handshake"
                        )
        finally:
            if not tunneling:
                conn.close()

    def _start_tunnel(self, client_conn: socket.socket, connect_message: str):
        parts = connect_message.split(" ")
        host_port = parts[1]
        host, port_str = host_port.rsplit(":", 1)
        remote_port = int(port_str)

        logger.info(f"[RETRO] Tunneling to {host}:{remote_port}")

        if self.socks5_host and self.socks5_port:
            remote_sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.set_proxy(
                socks.SOCKS5,
                addr=self.socks5_host,
                port=self.socks5_port,
                username=self.socks5_username,
                password=self.socks5_password,
                rdns=False,
            )
        else:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.interface_ip is not None:
            remote_sock.bind((self.interface_ip, 0))

        remote_sock.connect((host, remote_port))

        def forward(src: socket.socket, dst: socket.socket):
            try:
                while True:
                    chunk = src.recv(4096)
                    if not chunk:
                        break
                    dst.sendall(chunk)
            except ConnectionAbortedError:
                pass
            finally:
                src.close()
                dst.close()

        Thread(target=forward, args=(client_conn, remote_sock), daemon=True).start()
        Thread(target=forward, args=(remote_sock, client_conn), daemon=True).start()
