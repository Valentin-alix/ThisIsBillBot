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
from src.core.bot.lifecycle.scheduler import is_in_playtime
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.utils.run_in_background import Worker, run_in_background
from src.utils.internet import has_internet_connection


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
        self.ankama_launcher.start()

    def on_launch_account(self, login: str):
        self._thread_worker_runnings.append(
            run_in_background(lambda: self.relaunch_account(login))
        )

    def relaunch_account(self, login: str):
        related_bot = next(
            bot
            for _, bot in self.bot_by_account_id.items()
            if bot.account["apikey"]["login"] == login
        )
        if self._is_lauching_by_login[login].is_set():
            return related_bot.logger.warning(
                "Bot is already launching, don't launch twice."
            )

        self._is_lauching_by_login[login].set()

        related_bot.logger.info("relaunching this")

        now = datetime.now()

        related_bot.process_manager.kill_process()

        while not has_internet_connection():
            related_bot.logger.info("waiting for internet connection to be up")
            sleep(1)

        if (
            not related_bot.from_manual_play.is_set()
            and related_bot.bot_config
            and not is_in_playtime(
                now,
                related_bot.bot_config.playtime_starts,
                related_bot.bot_config.playtime_ends,
            )
        ):
            return related_bot.logger.info("Bot is not in playtime anymore")

        related_bot.logger.info("Launch bot")
        related_bot.process_manager.pid = self.ankama_launcher.launch_dofus(
            login, MITM_CONFIG_URL
        )

        related_bot.logger.info(f"pid {related_bot.process_manager.pid}")

        self._is_lauching_by_login[login].clear()

    def safe_stop_bots(self, bots: list[Bot]):
        threads = [
            threading.Thread(target=bot.behavior_coordinator.safe_stop, daemon=True)
            for bot in bots
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def get_bot_by_account_id(self) -> dict[int, Bot]:
        bot_by_account_id: dict[int, Bot] = {}
        for account in CryptoHelper.getStoredApiKeys():
            account_id = account["apikey"]["accountId"]
            bot_by_account_id[account_id] = BotFactory.create_bot(
                shared_signals=self.shared_signals,
                account=account,
            )
        return bot_by_account_id
