import logging
from dataclasses import dataclass, field
from socket import socket as Socket

from ankama_launcher_emulator_premium.proxy.dofus3.proxy import Proxy
from ankama_launcher_emulator_premium.proxy.dofus3.proxy_listener import (
    ProxyListener as BaseProxyListener,
)

from src.const import CONNECTION_SERVERS_IPS
from src.controller.bot_config import BotConfigController
from src.core.bot.bot import Bot
from src.core.mitm.connection_proxy import ConnectionProxy
from src.core.mitm.game_proxy import GameProxy

logger = logging.getLogger()


@dataclass(init=False)
class ProxyListener(BaseProxyListener):
    account_by_id: dict[int, Bot]
    account_by_port: dict[int, Bot] = field(init=False)
    _account_by_connection_port: dict[int, Bot] = field(init=False)

    def __init__(
        self,
        account_by_id: dict[int, Bot],
        socks5_host: str | None = None,
        socks5_port: int | None = None,
        socks5_username: str | None = None,
        socks5_password: str | None = None,
    ) -> None:
        super().__init__(
            socks5_host=socks5_host,
            socks5_port=socks5_port,
            socks5_username=socks5_username,
            socks5_password=socks5_password,
        )
        self.account_by_id = account_by_id
        self.account_by_port = {}
        self._account_by_connection_port = {}

    def on_connection_port_assigned(self, login: str, connection_port: int) -> None:
        related_bot = next(
            (
                bot
                for bot in self.account_by_id.values()
                if bot.account["apikey"]["login"] == login
            ),
            None,
        )
        if related_bot is not None:
            self._account_by_connection_port[connection_port] = related_bot

    def create_bridge(
        self, client_socket: Socket, server_socket: Socket, host_port: int
    ) -> Proxy | None:
        if server_socket.getpeername()[0] in CONNECTION_SERVERS_IPS:
            related_bot = self._account_by_connection_port.get(host_port)
            if related_bot is None:
                logger.warning("Did not find bot for connection port %d", host_port)
                return None

            def on_game_connection_callback(
                target_address: tuple[str, int], bot: Bot
            ) -> int:
                interface_ip = self.get_bot_network_interface(bot)
                port = self.start_game_listener(
                    target_address, interface_ip=interface_ip
                )
                self.account_by_port[port] = bot
                return port

            return ConnectionProxy(
                bot=related_bot,
                on_game_connection_callback=on_game_connection_callback,
                client_socket=client_socket,
                server_socket=server_socket,
                bot_by_id=self.account_by_id,
            )
        return GameProxy(
            bot=self.account_by_port[client_socket.getsockname()[1]],
            client_socket=client_socket,
            server_socket=server_socket,
        )

    def get_bot_network_interface(self, bot: Bot | None) -> str | None:
        if bot is None:
            return None
        login = bot.account["apikey"]["login"]
        configs = BotConfigController().get_bot_config_by_login()
        config = configs.get(login)
        return config.network_interface if config else None
