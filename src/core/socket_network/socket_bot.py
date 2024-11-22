"""Standalone CLI entry point for the socket-based bot.

Usage:
    uv run python -m src.core.socket_network.socket_bot <username> <password>

This module provides a headless alternative to the MITM approach: it connects
directly to Ankama's servers via TCP without requiring the Dofus client to run.
"""

import asyncio
import logging
import sys
import threading

from PyQt6.QtCore import QCoreApplication, QTimer
from PyQt6.QtWidgets import QApplication

from ankama_launcher_emulator.interfaces.deciphered_api_key import (
    DecipheredApiKey,
    DecipheredApiKeyDatas,
)
from ankama_launcher_emulator.interfaces.deciphered_cert import DecipheredCertifDatas

from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.socket_network.connection_client import ConnectionClient
from src.core.socket_network.game_client import GameClient

logger = logging.getLogger(__name__)


def _make_fake_account(login: str) -> DecipheredApiKey:
    fake_cert: DecipheredCertifDatas = {
        "id": 0,
        "encodedCertificate": "",
        "login": login,
    }
    fake_apikey: DecipheredApiKeyDatas = {
        "key": "",
        "provider": "ankama",
        "refreshToken": "",
        "isStayLoggedIn": False,
        "accountId": 0,
        "login": login,
        "certificate": fake_cert,
        "refreshDate": 0,
    }
    return {
        "apikeyFile": "",
        "apikey": fake_apikey,
    }


def run(username: str, password: str) -> None:
    from AnkamaLauncherEmulator.ankama_launcher_emulator.haapi.browser_oauth_authenticator import (
        authenticate,
    )

    app = QApplication(sys.argv)

    logger.info("[SocketBot] Authenticating via OAuth...")
    _, game_token = asyncio.run(authenticate(username, password))
    logger.info("[SocketBot] Authentication successful")

    account = _make_fake_account(username)
    shared_signals = SharedSignals()
    bot = BotFactory.create_bot(shared_signals, account)

    def start_connection() -> None:
        try:
            logger.info("[SocketBot] Connecting to login server...")
            host, port, ticket = ConnectionClient().connect(game_token)

            logger.info("[SocketBot] Connecting to game server...")
            GameClient().connect(host, port, ticket, bot)

            logger.info("[SocketBot] Bot is now in-game")
            bot.start()
        except Exception:
            logger.exception("[SocketBot] Connection failed")

    thread = threading.Thread(target=start_connection, daemon=True)
    thread.start()

    sys.exit(app.exec())


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    run(username, password)


if __name__ == "__main__":
    main()
