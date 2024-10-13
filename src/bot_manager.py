import json
import threading
from dataclasses import dataclass, field
from functools import partial
from time import sleep

import psutil
import requests
from PyQt5.QtCore import QThread
from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.consts import OFFICIAL_CONFIG_URL
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper

from src.bot import Bot
from src.bot_factory import BotFactory
from src.common.internet import has_internet_connection
from src.const import MITM_CONFIG_URL
from src.gui.utils.run_in_background import run_in_background, Worker
from src.interfaces.models.barrier import SubjectBarrier
from src.signals.shared_farm_signals import SharedSignals
from src.signals.shared_subjects import SharedSubjects


@dataclass
class BotManager:
    shared_signals: SharedSignals
    shared_subjects: SharedSubjects
    ankama_launcher_handler: AnkamaLauncherHandler = field(
        init=False, default_factory=AnkamaLauncherHandler
    )
    _thread_worker_runnings: list[tuple[QThread, Worker]] = field(
        default_factory=list, init=False
    )

    def __post_init__(self):
        self.ankama_launcher = AnkamaLauncherServer(self.ankama_launcher_handler)
        self.init_mitm_config()
        self.bot_by_account_id = self.get_bot_by_account_id()
        self.shared_signals.play_fighter.connect(self.on_play_fighter)
        self.shared_signals.launch_account.connect(self.on_launch_account)
        self.ankama_launcher.start()

    def init_mitm_config(self):
        response = requests.get(OFFICIAL_CONFIG_URL)
        response.raise_for_status()
        datas = response.json()
        datas["connectionHosts"] = ["JMBouftou:localhost:5555"]
        with open(MITM_CONFIG_URL, "w+") as config_file:
            config_file.write(json.dumps(datas))

    def on_play_fighter(
        self,
        account_id: int,
        area_id: int | None,
        sub_area_id: int | None,
        mule_bots: list["Bot"] | None,
    ):
        bot = self.bot_by_account_id[account_id]
        bot.stop_running_behaviors()
        bot.bot_signals.play.emit()
        if mule_bots is None:
            mule_bots = []
        bot.fighter_behavior.ready_barrier.set_target(len(mule_bots) + 1)
        bot.logger.info(f"Starting fighter with {len(mule_bots)} mules")

        self.safe_stop_bots(mule_bots)

        for mule in mule_bots:
            mule.bot_signals.play_mule.emit(area_id, sub_area_id)
            mule.play_action(
                lambda: mule.mule_fighter_behavior.start(
                    callback=partial(
                        self.on_mule_fighter_behavior_finished,
                        mule=mule,
                        leader_account_id=account_id,
                    ),
                    parent=None,
                    leader_id=bot.game_state.player.character_id,
                    ready_barrier=bot.fighter_behavior.ready_barrier,
                )
            )

        bot.logger.info("Mules are ready, starting leader fighter")
        bot.play_action(
            lambda: bot.fighter_behavior.start(
                callback=partial(
                    self.on_leader_fighter_behavior_finished,
                    mule_bots=mule_bots,
                ),
                parent=None,
                area_id=area_id,
                sub_area_id=sub_area_id,
                mule_states=[mule_bot.game_state for mule_bot in mule_bots],
            )
        )

    def on_leader_fighter_behavior_finished(
        self, error_code: str | None, mule_bots: list[Bot]
    ):
        for bot in mule_bots:
            bot.bot_signals.stop.emit()

    def on_mule_fighter_behavior_finished(
        self, error_code: str | None, mule: Bot, leader_account_id: int
    ):
        mule.bot_signals.stop.emit()
        leader_bot = self.bot_by_account_id[leader_account_id]
        leader_bot.fighter_behavior.mule_states = [
            mule_state
            for mule_state in leader_bot.fighter_behavior.mule_states
            if mule_state.player.character_id != mule.game_state.player.character_id
        ]
        leader_bot.fighter_behavior.ready_barrier.set_target(
            len(leader_bot.fighter_behavior.mule_states) + 1
        )

    def on_launch_account(self, login: str):
        self._thread_worker_runnings.append(
            run_in_background(lambda: self.relaunch_account(login))
        )

    def relaunch_account(self, login: str):
        related_bot = next(
            bot
            for account_id, bot in self.bot_by_account_id.items()
            if bot.account["apikey"]["login"] == login
        )
        if related_bot.pid is not None:
            try:
                process = psutil.Process(related_bot.pid)
                process.terminate()
                try:
                    process.wait(timeout=5)
                except psutil.TimeoutExpired:
                    related_bot.logger.info("timeout, force kill process")
                    process.kill()
                related_bot.logger.info(f"killed pid : {related_bot.pid}")
            except psutil.NoSuchProcess:
                related_bot.logger.info(
                    "process of related pid is not running anymore, skip."
                )
            related_bot.pid = None

        while not has_internet_connection():
            related_bot.logger.info("waiting for internet connection to be up")
            sleep(1)

        related_bot.logger.info("Launch bot")
        related_bot.pid = self.ankama_launcher.launch_dofus(login, MITM_CONFIG_URL)

    def safe_stop_bots(self, bots: list[Bot]):
        threads = [threading.Thread(target=bot.safe_stop, daemon=True) for bot in bots]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def get_bot_by_account_id(self) -> dict[int, Bot]:
        bot_by_account_id: dict[int, Bot] = {}
        ready_barrier = SubjectBarrier()
        for account in CryptoHelper.getStoredApiKeys():
            account_id = account["apikey"]["accountId"]
            bot_by_account_id[account_id] = BotFactory.create_bot(
                ready_barrier=ready_barrier,
                shared_signals=self.shared_signals,
                shared_subjects=self.shared_subjects,
                account=account,
            )
        return bot_by_account_id
