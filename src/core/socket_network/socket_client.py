import logging
from dataclasses import dataclass, field
from typing import Callable

from ankama_launcher_emulator_premium.haapi.haapi import Haapi

from src.controller.bot_config import BotConfig
from src.core.behaviors.socket.connection_behavior import (
    ConnectionErrorCode,
    IdentificationSuccessInfo,
)
from src.core.bot.bot import Bot
from src.core.socket_network.connection_client import ConnectionClient
from src.core.socket_network.game_client import GameClient

logger = logging.getLogger()


@dataclass
class SocketClient:
    bot: Bot
    bot_config: BotConfig
    socks_proxy_url: str | None
    on_banned_callback: Callable[[str], None]
    _connection_client: ConnectionClient | None = field(init=False, default=None)

    def connect(self) -> None:
        logger.info(f"Connecting socket client {self.bot.account.apikey.login}")
        account = self.bot.account
        game_token = Haapi(
            api_key=account.apikey.key,
            login=account.apikey.login,
            proxy_url=self.socks_proxy_url,
        ).createToken(1, account.apikey.certificate)
        logger.info(f"got game token {game_token}")
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
            self._connection_client.close()
        if error_code:
            if error_code == ConnectionErrorCode.BANNED:
                self.on_banned_callback(self.bot.account.apikey.login)
            return self.bot.logger.error(
                f"[SocketClient] Connection failed: {error_code}"
            )
        GameClient(
            bot=self.bot,
            proxy_url=self.socks_proxy_url,
        ).connect(
            identification_sucess_info.host,
            identification_sucess_info.port,
            identification_sucess_info.ticket,
        )
