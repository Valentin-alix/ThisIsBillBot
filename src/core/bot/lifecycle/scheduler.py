import threading
from dataclasses import dataclass, field
from datetime import datetime
from threading import Event, Thread
from time import sleep
from typing import Any

import schedule
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey
from PyQt5.QtCore import QThread

from D3Mapping.d3_mapping.signals.message_signals import MessageInfoSignals
from src.controller.bot_config import BotConfig
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.bot.execution.process_manager import ProcessManager
from src.core.signals.bot_signals import BotSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.logging.logger import Logger
from src.utils.internet import has_internet_connection


@dataclass
class BotScheduler:
    """Handles bot scheduling and playtime management."""

    logger: Logger
    account: DecipheredApiKey
    bot_signals: BotSignals
    shared_signals: SharedSignals
    log_signals: LogSignals
    is_playing_event: Event
    msg_info_signals: MessageInfoSignals

    bot_config: BotConfig | None

    behavior_coordinator: BehaviorCoordinator
    process_manager: ProcessManager

    _thread_worker_runnings: list[tuple[QThread, Any]] = field(
        init=False, default_factory=list
    )

    def start(self):
        """Start the bot scheduler if bot config exists."""
        if self.bot_config is not None:
            self.thread_planning = Thread(target=self.start_planning_bot, daemon=True)
            self.thread_planning.start()
            now = datetime.now()

            if is_in_playtime(
                now, self.bot_config.playtime_starts, self.bot_config.playtime_ends
            ):
                self.bot_signals.play.emit(False)
                self.shared_signals.launch_account.emit(self.account["apikey"]["login"])

    def start_planning_bot(self):
        """Setup scheduled tasks for bot playtime management."""

        def planned_stop_bot():
            self.logger.info("Stopping bot")
            self.log_signals.clear_logs.emit()
            if self.msg_info_signals:
                self.msg_info_signals.clear_msg_infos.emit()
            if self.is_playing_event.is_set():
                if self.behavior_coordinator:
                    self.behavior_coordinator.safe_stop()
                self.bot_signals.stop.emit()
                if self.process_manager:
                    self.process_manager.kill_process()
            else:
                self.logger.info("Bot is not playing, dont stop")

        def planned_restart_bot():
            self.logger.info("Restarting bot")
            now = datetime.now()
            while not has_internet_connection():
                self.logger.info(
                    "waiting for internet connection to be up in restart bot"
                )
                sleep(1)
            if self.bot_config and not is_in_playtime(
                now, self.bot_config.playtime_starts, self.bot_config.playtime_ends
            ):
                return self.logger.info("Bot is not anymore in playtime")

            if not self.is_playing_event.is_set():
                self.bot_signals.play.emit(False)
                self.logger.info("relaunching from planning")
                self.shared_signals.launch_account.emit(self.account["apikey"]["login"])
            else:
                self.logger.info("Bot is playing, dont restart")

        assert self.bot_config is not None
        for playtime_end in self.bot_config.playtime_ends:
            schedule.every().day.at(playtime_end).do(
                lambda: self._thread_worker_runnings.append(
                    run_in_background(planned_stop_bot)
                )
            )

        for playtime_start in self.bot_config.playtime_starts:
            schedule.every().day.at(playtime_start).do(
                lambda: self._thread_worker_runnings.append(
                    run_in_background(planned_restart_bot)
                )
            )


def run_continuously(interval=5):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        def run(self):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def is_in_playtime(
    now: datetime, playtime_starts: list[str], playtime_ends: list[str]
) -> bool:
    current_time = now

    current_date = datetime.now()

    for start_str, end_str in zip(playtime_starts, playtime_ends):
        start_hour, start_min = start_str.split(":")
        start = datetime(
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            hour=int(start_hour),
            minute=int(start_min),
        )
        end_hour, end_min = end_str.split(":")
        end = datetime(
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            hour=int(end_hour),
            minute=int(end_min),
        )

        if start <= end:
            if start <= current_time <= end:
                return True
        else:
            if current_time >= start or current_time <= end:
                return True

    return False
