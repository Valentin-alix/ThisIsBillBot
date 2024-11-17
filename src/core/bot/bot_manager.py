import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from time import sleep

from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from PyQt5.QtCore import QThread

from src.const import MITM_CONFIG_URL
from src.core.bot.bot import Bot
from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.utils.run_in_background import Worker, run_in_background
from src.utils.internet import ETHER_IP, has_internet_connection


@dataclass
class BotManager:
    shared_signals: SharedSignals
    ankama_launcher_handler: AnkamaLauncherHandler = field(
        init=False, default_factory=AnkamaLauncherHandler
    )
    _thread_worker_runnings: list[tuple[QThread, Worker]] = field(
        default_factory=list, init=False
    )
    _is_lauching_by_login: defaultdict[str, threading.Event] = field(
        default_factory=lambda: defaultdict(threading.Event), init=False
    )

    def __post_init__(self):
        self.ankama_launcher = AnkamaLauncherServer(self.ankama_launcher_handler)
        self.bot_by_account_id = self.get_bot_by_account_id()
        self.shared_signals.launch_account.connect(self.on_launch_account)
        self.shared_signals.synchronize_bots.connect(self.on_synchronize_bots)
        self.ankama_launcher.start(source_ip=ETHER_IP or "0.0.0.0")

    def on_launch_account(self, login: str):
        self._cleanup_finished_threads()

        thread, worker = run_in_background(lambda: self.relaunch_account(login))

        worker.signals.function_result.connect(lambda: self._remove_thread(thread))

        self._thread_worker_runnings.append((thread, worker))
        self._emit_thread_count()

    def _cleanup_finished_threads(self):
        self._thread_worker_runnings = [
            (_thread, _worker)
            for _thread, _worker in self._thread_worker_runnings
            if _thread.isRunning()
        ]
        self._emit_thread_count()

    def _remove_thread(self, thread: QThread):
        self._thread_worker_runnings = [
            (_thread, _worker)
            for _thread, _worker in self._thread_worker_runnings
            if _thread != thread
        ]
        self._emit_thread_count()

    def _emit_thread_count(self):
        count = len(self._thread_worker_runnings)
        self.shared_signals.thread_count_update.emit(count)

    def relaunch_account(self, login: str, max_retries: int = 10):
        related_bot: Bot = next(
            bot
            for _, bot in self.bot_by_account_id.items()
            if bot.account["apikey"]["login"] == login
        )
        if self._is_lauching_by_login[login].is_set():
            return related_bot.logger.warning(
                "Bot is already launching, don't launch twice."
            )

        self._is_lauching_by_login[login].set()

        for attempt in range(max_retries):
            related_bot.logger.info(
                f"Relaunching (attempt {attempt + 1}/{max_retries})"
            )

            now = datetime.now()

            related_bot.process_manager.kill_process()

            while not has_internet_connection():
                related_bot.logger.info("waiting for internet connection to be up")
                sleep(1)

            if related_bot.bot_should_not_play(now):
                self._is_lauching_by_login[login].clear()
                return related_bot.logger.info("Bot is not in playtime anymore")

            related_bot.logger.info("Launch bot")
            related_bot.process_manager.pid = self.ankama_launcher.launch_dofus(
                login, MITM_CONFIG_URL
            )

            related_bot.logger.info(f"Pid {related_bot.process_manager.pid}")

            is_sucess = related_bot.wait_for_connection_result(timeout=90)

            if related_bot.bot_should_not_play(now):
                self._is_lauching_by_login[login].clear()
                return related_bot.logger.info("Bot is not in playtime anymore")

            if is_sucess:
                self._is_lauching_by_login[login].clear()
                return related_bot.logger.info("Successfully connected")

            related_bot.logger.warning(f"Connection timeout on attempt {attempt + 1}")
            backoff = min(2**attempt * 5, 60)
            related_bot.logger.info(f"Retrying in {backoff}s...")
            sleep(backoff)

        self._is_lauching_by_login[login].clear()
        related_bot.logger.error(
            f"Failed to connect after {max_retries} attempts - stopping bot"
        )
        related_bot.is_playing_event.clear()
        related_bot.process_manager.kill_process()

    def safe_stop_bots(self, bots: list[Bot]):
        for bot in bots:
            bot.behavior_coordinator.stop_behaviors()

    def get_bot_by_account_id(self) -> dict[int, Bot]:
        bot_by_account_id: dict[int, Bot] = {}
        for account in CryptoHelper.getStoredApiKeys():
            account_id = account["apikey"]["accountId"]
            bot_by_account_id[account_id] = BotFactory.create_bot(
                shared_signals=self.shared_signals,
                account=account,
            )
        return bot_by_account_id

    def shutdown(self) -> None:
        for thread, _ in self._thread_worker_runnings:
            thread.quit()
            thread.wait(5000)
        self._thread_worker_runnings.clear()
        bots = list(self.bot_by_account_id.values())
        self.safe_stop_bots(bots)
        for bot in bots:
            bot.connection_handler.cleanup()
            bot.process_manager.kill_process()

    def on_synchronize_bots(self) -> None:
        for account in CryptoHelper.getStoredApiKeys():
            account_id = account["apikey"]["accountId"]
            if account_id not in self.bot_by_account_id:
                new_bot = BotFactory.create_bot(
                    shared_signals=self.shared_signals,
                    account=account,
                )
                self.bot_by_account_id[account_id] = new_bot
                new_bot.start()
                self.shared_signals.new_bot_added.emit(new_bot)
