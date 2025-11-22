import json
import logging
import socket
import threading

from src.core.bot.bot import Bot
from src.services.sandbox.executor import SandboxExecutor, SandboxResult

END_SENTINEL = "---END---"
_RECV_CHUNK_SIZE = 4096
_CONNECTION_TIMEOUT_SECONDS = 30

logger = logging.getLogger(__name__)


def _format_result(result: SandboxResult) -> str:
    payload: dict[str, str | None] = {"stdout": result.stdout, "result": result.result_repr, "error": result.error}
    return json.dumps(payload) + "\n"


def _bot_status(account_id: int, bot: Bot) -> dict[str, object]:
    running_behaviors = bot.behavior_coordinator.running_top_level_behaviors()
    return {
        "login": bot.account.apikey.login,
        "account_id": account_id,
        "connected": bot.is_connected_event.is_set(),
        "in_fight": bot.game_state.fight.in_fight,
        "current_behavior": running_behaviors[0].__class__.__name__ if running_behaviors else None,
    }


class SandboxServer:
    def __init__(self, bot_by_account_id: dict[int, Bot], port: int) -> None:
        self._bot_by_account_id = bot_by_account_id
        self._port = port
        self._socket: socket.socket | None = None
        self._accept_thread: threading.Thread | None = None
        self._stopping = threading.Event()

    def start(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("127.0.0.1", self._port))
        server_socket.listen()
        self._socket = server_socket

        self._accept_thread = threading.Thread(
            target=self._accept_loop, name="sandbox-server-accept", daemon=True
        )
        self._accept_thread.start()
        logger.info("Sandbox server listening on 127.0.0.1:%d", self._port)

    def stop(self) -> None:
        self._stopping.set()
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def _accept_loop(self) -> None:
        server_socket = self._socket
        if server_socket is None:
            return
        while not self._stopping.is_set():
            try:
                connection, _ = server_socket.accept()
            except OSError:
                return
            connection.settimeout(_CONNECTION_TIMEOUT_SECONDS)
            threading.Thread(
                target=self._handle_connection, args=(connection,), name="sandbox-server-conn", daemon=True
            ).start()

    def _find_bot(self, login: str) -> Bot | None:
        return next(
            (bot for bot in self._bot_by_account_id.values() if bot.account.apikey.login == login),
            None,
        )

    def _handle_connection(self, connection: socket.socket) -> None:
        with connection:
            buffer = ""
            try:
                buffer = self._read_until_newline(connection, buffer)
            except (ConnectionError, TimeoutError):
                return
            selection, buffer = buffer.split("\n", 1)
            selection = selection.strip()

            if selection == "list":
                bots = [
                    _bot_status(account_id, bot) for account_id, bot in self._bot_by_account_id.items()
                ]
                connection.sendall((json.dumps({"bots": bots}) + "\n").encode())
                return

            bot = self._find_bot(selection)
            if bot is None:
                error_payload: dict[str, str | None] = {
                    "stdout": "",
                    "result": None,
                    "error": f"Unknown bot login {selection!r}",
                }
                connection.sendall((json.dumps(error_payload) + "\n").encode())
                return

            try:
                buffer = self._read_until_sentinel(connection, buffer)
            except (ConnectionError, TimeoutError):
                return
            code = buffer.rsplit(f"\n{END_SENTINEL}\n", 1)[0]

            result = SandboxExecutor(bot=bot).run(code)
            connection.sendall(_format_result(result).encode())

    def _read_until_newline(self, connection: socket.socket, buffer: str) -> str:
        while "\n" not in buffer:
            chunk = connection.recv(_RECV_CHUNK_SIZE)
            if not chunk:
                raise ConnectionError("Client disconnected before selecting a bot")
            buffer += chunk.decode(errors="replace")
        return buffer

    def _read_until_sentinel(self, connection: socket.socket, buffer: str) -> str:
        sentinel = f"\n{END_SENTINEL}\n"
        while sentinel not in buffer:
            chunk = connection.recv(_RECV_CHUNK_SIZE)
            if not chunk:
                raise ConnectionError("Client disconnected before sending the end sentinel")
            buffer += chunk.decode(errors="replace")
        return buffer
