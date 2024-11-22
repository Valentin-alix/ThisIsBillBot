import random
import threading
from dataclasses import dataclass, field
from datetime import datetime, time
from threading import Event
from time import sleep
from typing import Any, Callable

import schedule

SCHEDULE_RANDOM_MINUTES_MIN = 1
SCHEDULE_RANDOM_MINUTES_MAX = 8

from ankama_launcher_emulator.interfaces.deciphered_api_key import (
    DecipheredApiKey,
)
from PyQt6.QtCore import QThread

from src.controller.bot_config import BotConfig
from src.controller.schedule_profile_controller import ScheduleProfileController
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.bot.execution.process_manager import ProcessManager
from src.core.signals.bot_signals import BotSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.message_signals import MessageInfoSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.utils.run_in_background import run_in_background
from src.services.logging.contextual_logger import ContextualLogger
from src.utils.internet import has_internet_connection

DAY_SCHEDULERS = {
    0: lambda: schedule.every().monday,
    1: lambda: schedule.every().tuesday,
    2: lambda: schedule.every().wednesday,
    3: lambda: schedule.every().thursday,
    4: lambda: schedule.every().friday,
    5: lambda: schedule.every().saturday,
    6: lambda: schedule.every().sunday,
}


@dataclass
class RandomizedSlot:
    start: str
    end: str


@dataclass
class BotScheduler(ContextualLogger):
    """Handles bot scheduling and playtime management."""

    account: DecipheredApiKey
    bot_signals: BotSignals
    shared_signals: SharedSignals
    log_signals: LogSignals
    is_playing_event: Event
    msg_info_signals: MessageInfoSignals

    get_bot_config: Callable[[], BotConfig | None]

    behavior_coordinator: BehaviorCoordinator
    process_manager: ProcessManager

    _thread_worker_runnings: list[tuple[QThread, Any]] = field(
        init=False, default_factory=list
    )
    _scheduled_jobs: list[schedule.Job] = field(init=False, default_factory=list)
    _randomized_slots_by_day: dict[int, list[RandomizedSlot]] = field(
        init=False, default_factory=dict
    )

    def start(self):
        """Start the bot scheduler if bot config exists."""
        config = self.get_bot_config()
        if config is None or config.schedule_profile is None:
            return

        self._schedule_profile_jobs(config.schedule_profile)

        now = datetime.now()
        if self.is_in_randomized_playtime(now):
            self.bot_signals.play.emit(False)
            self.shared_signals.launch_account.emit(self.account["apikey"]["login"])

    def update_profile(self, profile_id: str | None):
        """Update the schedule profile and reschedule jobs."""
        config = self.get_bot_config()
        if config is None:
            config = BotConfig(schedule_profile=profile_id)
        else:
            config.schedule_profile = profile_id

        self._clear_scheduled_jobs()

        if profile_id is None:
            if self.is_playing_event.is_set():
                self._thread_worker_runnings.append(
                    run_in_background(self._planned_stop_bot)
                )
            return

        self._schedule_profile_jobs(profile_id)

        now = datetime.now()
        self.logger.info(f"Profile updated to {profile_id}, checking playtime...")

        if self.is_in_randomized_playtime(now):
            self.logger.info(
                f"In playtime, is_playing: {self.is_playing_event.is_set()}"
            )
            if not self.is_playing_event.is_set():
                self.logger.info("Starting bot...")
                self.bot_signals.play.emit(False)
                self.shared_signals.launch_account.emit(self.account["apikey"]["login"])
        elif self.is_playing_event.is_set():
            self.logger.info("Not in playtime, stopping bot...")
            self._thread_worker_runnings.append(
                run_in_background(self._planned_stop_bot)
            )

    def _clear_scheduled_jobs(self):
        """Cancel all scheduled jobs for this bot."""
        for job in self._scheduled_jobs:
            schedule.cancel_job(job)
        self._scheduled_jobs.clear()
        self._randomized_slots_by_day.clear()

    def _schedule_profile_jobs(self, profile_id: str):
        """Setup scheduled tasks for each time slot in the profile."""
        profile = ScheduleProfileController().get_profile(profile_id)
        if not profile:
            return

        for day_str, slots in profile.slots_by_day.items():
            day = int(day_str)
            day_scheduler = DAY_SCHEDULERS[day]
            self._randomized_slots_by_day[day] = []

            for slot in slots:
                start_time = _add_random_minutes(slot.start)
                end_time = _subtract_random_minutes(slot.end)

                self._randomized_slots_by_day[day].append(
                    RandomizedSlot(start=start_time, end=end_time)
                )

                self.logger.info(
                    f"Scheduling day {day}: start={start_time} (was {slot.start}), "
                    f"end={end_time} (was {slot.end})"
                )

                start_job = (
                    day_scheduler()
                    .at(start_time)
                    .do(
                        lambda: self._thread_worker_runnings.append(
                            run_in_background(self._planned_restart_bot)
                        )
                    )
                )
                self._scheduled_jobs.append(start_job)

                end_job = (
                    day_scheduler()
                    .at(end_time)
                    .do(
                        lambda: self._thread_worker_runnings.append(
                            run_in_background(self._planned_stop_bot)
                        )
                    )
                )
                self._scheduled_jobs.append(end_job)

        midnight_job = (
            schedule.every()
            .day.at("00:00")
            .do(lambda: self._reschedule_with_new_random_times(profile_id))
        )
        self._scheduled_jobs.append(midnight_job)

    def _reschedule_with_new_random_times(self, profile_id: str):
        """Reschedule all jobs with new random times (called daily at midnight)."""
        self.logger.info("Midnight reschedule: generating new random times")
        self._clear_scheduled_jobs()
        self._schedule_profile_jobs(profile_id)

    def is_in_randomized_playtime(self, now: datetime) -> bool | None:
        """Check if current time is within the randomized playtime slots.

        Returns None if no schedule profile is configured.
        """
        if not self._randomized_slots_by_day:
            return None

        day = now.weekday()
        slots = self._randomized_slots_by_day.get(day, [])
        if not slots:
            return False

        current_time = now.time()

        for slot in slots:
            start_hour, start_min = map(int, slot.start.split(":"))
            end_hour, end_min = map(int, slot.end.split(":"))

            start_time = time(hour=start_hour, minute=start_min)
            end_time = time(hour=end_hour, minute=end_min)

            if start_time <= end_time:
                if start_time <= current_time <= end_time:
                    return True
            else:
                if current_time >= start_time or current_time <= end_time:
                    return True

        return False

    def _planned_stop_bot(self):
        self.logger.info("Stopping bot")
        if self.is_playing_event.is_set():
            if self.behavior_coordinator:
                self.behavior_coordinator.stop_behaviors()
            self.bot_signals.stop.emit()
            if self.process_manager:
                self.process_manager.kill_process()
        else:
            self.logger.info("Bot is not playing, dont stop")

    def _planned_restart_bot(self):
        self.logger.info("Restarting bot")
        while not has_internet_connection():
            self.logger.info("waiting for internet connection to be up in restart bot")
            sleep(1)

        if not self.is_in_randomized_playtime(datetime.now()):
            return self.logger.info("Bot is not anymore in playtime")

        if not self.is_playing_event.is_set():
            self.bot_signals.play.emit(False)
            self.shared_signals.launch_account.emit(self.account["apikey"]["login"])
        else:
            self.logger.info("Bot is playing, dont restart")


def run_continuously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        def run(self):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def _add_random_minutes(time_str: str) -> str:
    """Add random minutes to a time string (delays start, eats into playtime)."""
    hours, minutes = map(int, time_str.split(":"))
    random_minutes = random.randint(
        SCHEDULE_RANDOM_MINUTES_MIN, SCHEDULE_RANDOM_MINUTES_MAX
    )
    total_minutes = hours * 60 + minutes + random_minutes
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60
    return f"{new_hours:02d}:{new_minutes:02d}"


def _subtract_random_minutes(time_str: str) -> str:
    """Subtract random minutes from a time string (stops earlier, eats into playtime)."""
    hours, minutes = map(int, time_str.split(":"))
    random_minutes = random.randint(
        SCHEDULE_RANDOM_MINUTES_MIN, SCHEDULE_RANDOM_MINUTES_MAX
    )
    total_minutes = hours * 60 + minutes - random_minutes
    if total_minutes < 0:
        total_minutes += 24 * 60
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60
    return f"{new_hours:02d}:{new_minutes:02d}"
