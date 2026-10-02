import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from socket import socket as Socket

from ankama_launcher_emulator.proxy.proxy import Proxy
from ankama_launcher_emulator.proxy.proxy_listener import (
    ProxyListener as BaseProxyListener,
)

from src.consts import get_connection_servers_ips
from src.controller.bot_config import BotConfigService
from src.core.bot.bot import Bot
from src.core.mitm.connection_proxy import ConnectionProxy
from src.core.mitm.game_proxy import GameProxy

logger = logging.getLogger()


@dataclass(init=False)
class ProxyListener(BaseProxyListener):
    account_by_id: dict[int, Bot]
    on_banned_callback: Callable[[str], None]
    account_by_port: dict[int, Bot] = field(init=False)
    _account_by_connection_port: dict[int, Bot] = field(init=False)

    def __init__(
        self,
        account_by_id: dict[int, Bot],
        on_banned_callback: Callable[[str], None],
    ) -> None:
        super().__init__()
        self.account_by_id = account_by_id
        self.on_banned_callback = on_banned_callback
        self.account_by_port = {}
        self._account_by_connection_port = {}

    def on_connection_port_assigned(self, login: str, connection_port: int) -> None:
        related_bot = next(
            (bot for bot in list(self.account_by_id.values()) if bot.account.apikey.login == login),
            None,
        )
        if related_bot is not None:
            self._account_by_connection_port[connection_port] = related_bot

    def create_bridge(self, client_socket: Socket, server_socket: Socket, host_port: int) -> Proxy | None:
        if server_socket.getpeername()[0] in get_connection_servers_ips():
            related_bot = self._account_by_connection_port.get(host_port)
            if related_bot is None:
                logger.warning("Did not find bot for connection port %d", host_port)
                return None

            def on_game_connection_callback(target_address: tuple[str, int], bot: Bot) -> int:
                proxy_url = self.get_bot_proxy_url(bot)
                port = self.start_game_listener(target_address, proxy_url=proxy_url)
                self.account_by_port[port] = bot
                return port

            return ConnectionProxy(
                bot=related_bot,
                on_game_connection_callback=on_game_connection_callback,
                client_socket=client_socket,
                server_socket=server_socket,
                bot_by_id=self.account_by_id,
                on_banned_callback=self.on_banned_callback,
            )
        return GameProxy(
            bot=self.account_by_port[client_socket.getsockname()[1]],
            client_socket=client_socket,
            server_socket=server_socket,
        )

    def get_bot_proxy_url(self, bot: Bot) -> str | None:
        login = bot.account.apikey.login
        configs = BotConfigService().get_bot_config_by_login()
        config = configs.get(login)
        assert config is not None, f"Bot {login} must have a configuration"
        if config.schedule_profile is None:
            return None
        return BotConfigService().resolve_bot_socks_proxy_url(config)
