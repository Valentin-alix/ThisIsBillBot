import json
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from time import sleep

import requests
from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.consts import OFFICIAL_CONFIG_URL
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from PyQt5.QtCore import QThread

from src.bot import Bot
from src.bot_factory import BotFactory
from src.common.internet import has_internet_connection
from src.const import MITM_CONFIG_URL
from src.gui.utils.run_in_background import Worker, run_in_background
from src.signals.shared_farm_signals import SharedSignals


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
        self.init_mitm_config()
        self.bot_by_account_id = self.get_bot_by_account_id()
        self.shared_signals.launch_account.connect(self.on_launch_account)
        self.ankama_launcher.start()

    def init_mitm_config(self):
        response = requests.get(OFFICIAL_CONFIG_URL)
        response.raise_for_status()
        datas = response.json()
        datas["connectionHosts"] = ["JMBouftou:localhost:5555"]
        with open(MITM_CONFIG_URL, "w+") as config_file:
            config_file.write(json.dumps(datas))

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

        related_bot.kill_process()

        while not has_internet_connection():
            related_bot.logger.info("waiting for internet connection to be up")
            sleep(1)

        related_bot.logger.info("Launch bot")
        related_bot.pid = self.ankama_launcher.launch_dofus(login, MITM_CONFIG_URL)

        related_bot.logger.info(f"pid {related_bot.pid}")

        self._is_lauching_by_login[login].clear()

    def safe_stop_bots(self, bots: list[Bot]):
        threads = [threading.Thread(target=bot.safe_stop, daemon=True) for bot in bots]
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
