import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from hashlib import sha256

from ankama_launcher_emulator_premium.haapi.haapi import Haapi
from requests import HTTPError

from src.controller.bot_config import BotConfig
from src.core.behaviors.socket.connection_behavior import (
    ConnectionErrorCode,
    IdentificationSuccessInfo,
)
from src.core.bot.bot import Bot
from src.core.socket_network.connection_client import ConnectionClient
from src.core.socket_network.game_client import GameClient

logger = logging.getLogger()


def _is_create_token_auth_failure(error: HTTPError) -> bool:
    message = str(error)
    return "Account/CreateToken" in message and (
        "403 Client Error" in message
        or "401 Client Error" in message
        or "Unauthorized service" in message
        or "Invalid security state" in message
    )


def _fingerprint_secret(secret: str) -> str:
    return sha256(secret.encode()).hexdigest()[:8]


@dataclass
class SocketClient:
    bot: Bot
    bot_config: BotConfig
    socks_proxy_url: str | None
    on_banned_callback: Callable[[str], None]
    on_invalid_auth_callback: Callable[[str], None]
    _connection_client: ConnectionClient | None = field(init=False, default=None)

    def connect(self) -> None:
        logger.info(f"Connecting socket client {self.bot.account.apikey.login}")
        account = self.bot.account
        try:
            game_token = Haapi(
                api_key=account.apikey.key,
                login=account.apikey.login,
                proxy_url=self.socks_proxy_url,
            ).createToken(1, account.apikey.certificate)
        except HTTPError as error:
            if not _is_create_token_auth_failure(error):
                raise
            logger.error(
                "[SocketClient] Stored HAAPI credentials rejected for %s: %s",
                account.apikey.login,
                error,
            )
            self.on_invalid_auth_callback(account.apikey.login)
            return
        logger.info(
            "[SocketClient] Got HAAPI game token "
            f"len={len(game_token)} fingerprint={_fingerprint_secret(game_token)}"
        )
        self._connection_client = ConnectionClient(
            bot=self.bot,
            connection_behavior=self.bot.connection_behavior,
            proxy_url=self.socks_proxy_url,
        )
        self._connection_client.connect(game_token, self.connected_server)

    def connected_server(
        self,
        error_code: str | None,
        identification_sucess_info: IdentificationSuccessInfo,
    ) -> None:
        if self._connection_client:
            self.bot.logger.info("[SocketClient] Closing connection client before game handoff")
            self._connection_client.close()
        if error_code:
            if error_code == ConnectionErrorCode.BANNED or error_code == 14:
                self.on_banned_callback(self.bot.account.apikey.login)
            return self.bot.logger.error(f"[SocketClient] Connection failed: {error_code}")
        self.bot.logger.info(
            "[SocketClient] Connection server handoff complete: "
            f"game_host={identification_sucess_info.host}, "
            f"game_port={identification_sucess_info.port}, "
            f"ticket_len={len(identification_sucess_info.ticket)}, "
            "ticket_fingerprint="
            f"{_fingerprint_secret(identification_sucess_info.ticket)}"
        )
        self.bot.logger.info("[SocketClient] Starting game client handoff")
        GameClient(
            bot=self.bot,
            proxy_url=self.socks_proxy_url,
        ).connect(
            identification_sucess_info.host,
            identification_sucess_info.port,
            identification_sucess_info.ticket,
        )
