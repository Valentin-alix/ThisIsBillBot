import logging
from dataclasses import dataclass, field
from socket import socket as Socket

from ankama_launcher_emulator.proxy.proxy import Proxy
from ankama_launcher_emulator.proxy.proxy_listener import (
    ProxyListener as BaseProxyListener,
)

from src.const import CONNECTION_SERVERS_IPS
from src.controller.bot_config import BotConfigController
from src.core.bot.bot import Bot
from src.core.mitm.connection_proxy import ConnectionProxy
from src.core.mitm.game_proxy import GameProxy
from src.utils.pids import get_pid_by_local_and_remote_port

logger = logging.getLogger()


@dataclass
class ProxyListener(BaseProxyListener):
    account_by_id: dict[int, Bot] = field(default_factory=dict)
    account_by_port: dict[int, Bot] = field(init=False, default_factory=dict)

    def create_bridge(
        self, client_socket: Socket, server_socket: Socket, host_port: int
    ) -> Proxy | None:
        if server_socket.getpeername()[0] in CONNECTION_SERVERS_IPS:
            local_port = client_socket.getpeername()[1]
            related_pid = get_pid_by_local_and_remote_port(
                local_port=local_port, remote_port=host_port
            )
            if related_pid is None:
                logger.warning("Did not found related pid")
                return None

            related_bot = next(
                (
                    bot
                    for bot in self.account_by_id.values()
                    if bot.process_manager.pid == related_pid
                ),
                None,
            )

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
