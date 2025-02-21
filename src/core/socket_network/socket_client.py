import logging
from dataclasses import dataclass, field

from ankama_launcher_emulator_premium.haapi.haapi import Haapi

from src.controller.bot_config import BotConfig
from src.core.bot.bot import Bot
from src.core.socket_network.connection_client import ConnectionClient
from src.core.socket_network.game_client import GameClient

logger = logging.getLogger()


@dataclass
class SocketClient:
    bot: Bot
    bot_config: BotConfig | None
    _connection_client: ConnectionClient | None = field(init=False, default=None)

    def connect(self) -> None:
        logger.info(
            f"Connecting socket client {self.bot.account['apikey']['login']}"
        )
        account = self.bot.account
        interface_ip = self.bot_config.network_interface if self.bot_config else None
        game_token = Haapi(
            api_key=account["apikey"]["key"],
            login=account["apikey"]["login"],
            interface_ip=interface_ip,
            proxy_url=None,
        ).createToken(1, account["apikey"]["certificate"])
        logger.info(f"got game token {game_token}")
        self._connection_client = ConnectionClient(
            bot=self.bot, connection_behavior=self.bot.connection_behavior
        )
        self._connection_client.connect(game_token, self.connected_server)

    def connected_server(
        self, error_code: str | None, host: str, port: int, ticket: str
    ) -> None:
        if self._connection_client:
            self._connection_client.close()
        if error_code:
            return self.bot.logger.error(
                f"[SocketClient] Connection failed: {error_code}"
            )
        GameClient(self.bot).connect(host, port, ticket)
