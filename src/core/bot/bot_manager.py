import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from time import monotonic, sleep

from ankama_launcher_emulator_premium.web.auth.storage import (
    mark_account_available_for_auth_retry,
    remove_generated_account,
)

LAUNCH_SPACING_SECONDS = 2.5
MITM_CONNECTION_WAIT_TIMEOUT_SECONDS = 90.0
MITM_CONNECTION_WAIT_STEP_SECONDS = 0.5

from ankama_launcher_emulator_premium.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator_premium.gui.utils import run_in_background
from ankama_launcher_emulator_premium.server.handler import AnkamaLauncherHandler
from ankama_launcher_emulator_premium.server.server import (
    AnkamaLauncherServer,
)

from src.controller.bot_config import BotConfig, BotConfigService
from src.core.bot.bot import Bot
from src.core.bot.bot_factory import BotFactory
from src.core.bot.lifecycle.account_scheduler import AccountScheduler
from src.core.mitm.proxy_listener import ProxyListener
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.socket_network.socket_client import SocketClient

logger = logging.getLogger()


@dataclass
class BotManager:
    shared_signals: SharedSignals
    enable_account_scheduler: bool = True
    ankama_launcher_handler: AnkamaLauncherHandler = field(
        init=False, default_factory=AnkamaLauncherHandler
    )
    _running_task_count: int = field(default=0, init=False)
    _is_lauching_by_login: defaultdict[str, threading.Event] = field(
        default_factory=lambda: defaultdict(threading.Event), init=False
    )
    _launch_lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _last_launch_time: float = field(default=0.0, init=False)

    def _wait_launch_slot(self) -> None:
        with self._launch_lock:
            wait = self._last_launch_time + LAUNCH_SPACING_SECONDS - monotonic()
            if wait > 0:
                sleep(wait)
            self._last_launch_time = monotonic()

    def __post_init__(self):
        self.ankama_launcher = AnkamaLauncherServer(self.ankama_launcher_handler)
        self.bot_by_account_id = self.get_bot_by_account_id()
        self.shared_signals.launch_account.connect(self.on_launch_account)
        self.shared_signals.synchronize_bots.connect(self.on_synchronize_bots)
        self.proxy_listener = ProxyListener(account_by_id=self.bot_by_account_id)
        self.account_scheduler = AccountScheduler(
            on_accounts_synchronized=self.shared_signals.synchronize_bots.emit,
            on_subscribed=self.on_subscribed,
            on_banned_callback=self.on_banned_callback,
        )
        if self.enable_account_scheduler:
            self.account_scheduler.start()

    def on_subscribed(self, login: str):
        related_bot = next(
            (
                bot
                for bot in self.bot_by_account_id.values()
                if bot.account.apikey.login == login
            ),
            None,
        )
        if not related_bot:
            logger.error(f"bot {login} not found in bot by account id ?")
            return
        if related_bot.is_playing_event.is_set():
            self.shared_signals.launch_account.emit(login)

    def on_launch_account(self, login: str):
        self._running_task_count += 1
        self._emit_thread_count()

        def _on_done(_: object) -> None:
            self._running_task_count -= 1
            self._emit_thread_count()

        run_in_background(
            lambda _: self.relaunch_account(login),
            on_success=_on_done,
            on_error=_on_done,
        )

    def on_progress_installing(self, text: str):
        print(f"In progress : {text}")

    def _emit_thread_count(self):
        self.shared_signals.thread_count_update.emit(self._running_task_count)

    def _get_socks_proxy_url(self, bot_config: BotConfig) -> str | None:
        if bot_config.schedule_profile is None:
            return None
        return BotConfigService().resolve_bot_socks_proxy_url(bot_config)

    def _wait_for_mitm_connection_result(self, bot: Bot) -> bool:
        deadline = monotonic() + MITM_CONNECTION_WAIT_TIMEOUT_SECONDS
        while monotonic() < deadline:
            if bot.is_connected_event.wait(timeout=MITM_CONNECTION_WAIT_STEP_SECONDS):
                return True
            if not bot.is_playing_event.is_set():
                bot.logger.info("Bot is not playing anymore, aborting relaunch")
                return False
            if not bot.process_manager.is_bot_process_running():
                bot.logger.info(
                    "Dofus process is not running anymore, aborting relaunch"
                )
                return False
        return False

    def relaunch_account(self, login: str, max_retries: int = 3):
        related_bot = next(
            (
                bot
                for _, bot in self.bot_by_account_id.items()
                if bot.account.apikey.login == login
            ),
            None,
        )
        if related_bot is None:
            self._is_lauching_by_login.pop(login, None)
            return None

        if self._is_lauching_by_login[login].is_set():
            launch_still_active = related_bot.is_playing_event.is_set() and (
                related_bot.process_manager.pid is None
                or related_bot.process_manager.is_bot_process_running()
            )
            if launch_still_active:
                return related_bot.logger.warning(
                    "Bot is already launching, don't launch twice."
                )
            self._is_lauching_by_login[login].clear()

        self._is_lauching_by_login[login].set()

        try:
            bot_config = BotConfigService().get_bot_config(
                related_bot.account.apikey.login
            )

            related_bot.process_manager.kill_process()

            if not related_bot.is_playing_event.is_set():
                return related_bot.logger.info(
                    "Bot is not playing anymore, aborting relaunch"
                )
            if related_bot.bot_should_not_play(datetime.now()):
                return related_bot.logger.info("Bot is not in playtime anymore")

            socks_proxy_url = self._get_socks_proxy_url(bot_config)
            for attempt in range(max_retries):
                if not related_bot.is_playing_event.is_set():
                    return related_bot.logger.info(
                        "Bot is not playing anymore, aborting relaunch"
                    )

                related_bot.logger.info(
                    f"Relaunching (attempt {attempt + 1}/{max_retries})"
                )

                now = datetime.now()

                if related_bot.bot_should_not_play(now):
                    return related_bot.logger.info("Bot is not in playtime anymore")

                related_bot.logger.info("Launch bot")
                self._wait_launch_slot()

                if bot_config.connection_mode == "socket":
                    SocketClient(
                        related_bot,
                        bot_config,
                        socks_proxy_url,
                        self.on_banned_callback,
                        self.on_invalid_auth_callback,
                    ).connect()
                    return
                related_bot.process_manager.pid = self.ankama_launcher.launch_dofus(
                    login,
                    self.proxy_listener,
                    proxy_url=socks_proxy_url,
                    on_progress=self.on_progress_installing,
                )
                related_bot.logger.info(f"Pid {related_bot.process_manager.pid}")
                is_success = self._wait_for_mitm_connection_result(related_bot)

                if not related_bot.is_playing_event.is_set():
                    return related_bot.logger.info(
                        "Bot is not playing anymore, aborting relaunch"
                    )
                if related_bot.bot_should_not_play(now):
                    return related_bot.logger.info("Bot is not in playtime anymore")

                if is_success:
                    return related_bot.logger.info("Successfully connected")

                related_bot.logger.warning(
                    f"Connection timeout on attempt {attempt + 1}"
                )
                backoff = min(2**attempt * 5, 60)
                related_bot.logger.info(f"Retrying in {backoff}s...")
                sleep(backoff)

            related_bot.logger.error(
                f"Failed to connect after {max_retries} attempts - stopping bot"
            )
            related_bot.is_playing_event.clear()
            related_bot.process_manager.kill_process()
        finally:
            self._is_lauching_by_login[login].clear()

    def on_banned_callback(self, login: str):
        CryptoHelper.remove_bot(login)
        BotConfigService().remove_bot_config(login)
        remove_generated_account(login)
        self.on_synchronize_bots()

    def on_invalid_auth_callback(self, login: str) -> None:
        mark_account_available_for_auth_retry(login)
        CryptoHelper.remove_bot(login)
        self.on_synchronize_bots()

    def safe_stop_bots(self, bots: list[Bot]):
        for bot in bots:
            bot.behavior_coordinator.stop_behaviors()

    def get_bot_by_account_id(self) -> dict[int, Bot]:
        bot_by_account_id: dict[int, Bot] = {}
        for account in CryptoHelper.getStoredApiKeys():
            account_id = account.apikey.accountId
            bot_by_account_id[account_id] = BotFactory.create_bot(
                shared_signals=self.shared_signals,
                account=account,
            )
        return bot_by_account_id

    def shutdown(self) -> None:
        if self.enable_account_scheduler:
            self.account_scheduler.stop()
        bots = list(self.bot_by_account_id.values())
        self.safe_stop_bots(bots)
        for bot in bots:
            bot.connection_handler.cleanup()
            bot.process_manager.kill_process()
        self.proxy_listener.shutdown()

    def _cleanup_removed_bot(self, bot: Bot) -> None:
        login = bot.account.apikey.login
        bot.scheduler.stop()
        bot.is_playing_event.clear()
        bot.behavior_coordinator.stop_behaviors()
        bot.connection_handler.cleanup()
        bot.process_manager.kill_process()
        self._is_lauching_by_login.pop(login, None)

    def on_synchronize_bots(self) -> None:
        account_by_id = {
            account.apikey.accountId: account
            for account in CryptoHelper.getStoredApiKeys()
        }

        removed_account_ids = set(self.bot_by_account_id) - set(account_by_id)
        for account_id in removed_account_ids:
            removed_bot = self.bot_by_account_id.pop(account_id)
            self._cleanup_removed_bot(removed_bot)
            self.shared_signals.bot_removed.emit(removed_bot)

        for account_id, account in account_by_id.items():
            if account_id not in self.bot_by_account_id:
                new_bot = BotFactory.create_bot(
                    shared_signals=self.shared_signals,
                    account=account,
                )
                self.bot_by_account_id[account_id] = new_bot
                self.shared_signals.new_bot_added.emit(new_bot)
                if self.enable_account_scheduler:
                    new_bot.start()
