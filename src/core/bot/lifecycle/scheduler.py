import random
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Event
from time import sleep

import schedule

SCHEDULE_RANDOM_MINUTES_MIN = 10
SCHEDULE_RANDOM_MINUTES_MAX = 30
MULE_SCHEDULE_RANDOM_MINUTES_MIN = 1
MULE_SCHEDULE_RANDOM_MINUTES_MAX = 8

from ankama_launcher_emulator_premium.gui.utils import run_in_background
from ankama_launcher_emulator_premium.interfaces.credentials import (
    StoredApiKey,
)
from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfileController,
)

from src.controller.bot_config import BotConfig
from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.bot.execution.process_manager import ProcessManager
from src.core.bot.kamas_mule_registry import KamasMuleRegistry
from src.core.events_manager.event_manager import EventManager
from src.core.signals.bot_signals import BotSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.message_signals import MessageInfoSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.services.logging_utils.contextual_logger import ContextualLogger


@dataclass
class RandomizedSlot:
    start: str
    end: str


@dataclass
class BotScheduler(ContextualLogger):
    """Handles bot scheduling and playtime management."""

    account: StoredApiKey
    bot_signals: BotSignals
    shared_signals: SharedSignals
    log_signals: LogSignals
    is_playing_event: Event
    msg_info_signals: MessageInfoSignals

    get_bot_config: Callable[[], BotConfig | None]

    behavior_coordinator: BehaviorCoordinator
    process_manager: ProcessManager
    event_manager: EventManager

    _scheduled_jobs: list[schedule.Job] = field(init=False, default_factory=list[schedule.Job])
    _randomized_slots_by_day: dict[int, list[RandomizedSlot]] = field(
        init=False, default_factory=dict[int, list[RandomizedSlot]]
    )
    _pending_mule_stop: threading.Timer | None = field(init=False, default=None)
    _is_kamas_mule_profile: bool = field(init=False, default=False)

    def start(self) -> None:
        """Start the bot scheduler if bot config exists."""
        config = self.get_bot_config()
        if config is None or config.schedule_profile is None:
            return

        self._schedule_profile_jobs(config.schedule_profile)

        now = datetime.now()
        if self.is_in_randomized_playtime(now):
            self.bot_signals.play.emit(False)
            self.shared_signals.launch_account.emit(self.account.apikey.login)

    def stop(self) -> None:
        if self._pending_mule_stop is not None:
            self._pending_mule_stop.cancel()
            self._pending_mule_stop = None
        if self._is_kamas_mule_profile:
            KamasMuleRegistry().mark_unavailable(self.account.apikey.login)
        self._clear_scheduled_jobs()

    def disconnect_now(self) -> None:
        """Disconnect the active runtime without waiting for schedule state."""
        run_in_background(self._manual_disconnect_bot_task)

    def _clear_scheduled_jobs(self) -> None:
        """Cancel all scheduled jobs for this bot."""
        for job in self._scheduled_jobs:
            schedule.cancel_job(job)
        self._scheduled_jobs.clear()
        self._randomized_slots_by_day.clear()

    def _schedule_profile_jobs(self, profile_id: str) -> None:
        """Setup scheduled tasks for each time slot in the profile."""
        profile = ScheduleProfileController().get_profile(profile_id)
        if not profile:
            self.logger.error(f"Unknown schedule profile {profile_id}")
            return
        self._is_kamas_mule_profile = profile.kind == "kamas_mule"
        random_minutes_min = (
            MULE_SCHEDULE_RANDOM_MINUTES_MIN
            if self._is_kamas_mule_profile
            else SCHEDULE_RANDOM_MINUTES_MIN
        )
        random_minutes_max = (
            MULE_SCHEDULE_RANDOM_MINUTES_MAX
            if self._is_kamas_mule_profile
            else SCHEDULE_RANDOM_MINUTES_MAX
        )

        for day_str, slots in profile.slots_by_day.items():
            day = int(day_str)
            self._randomized_slots_by_day[day] = []

            for slot in slots:
                start_time = _add_random_minutes(
                    slot.start,
                    random_minutes_min,
                    random_minutes_max,
                )
                end_time = _subtract_random_minutes(
                    slot.end,
                    random_minutes_min,
                    random_minutes_max,
                )

                self._randomized_slots_by_day[day].append(RandomizedSlot(start=start_time, end=end_time))

                self.logger.info(
                    f"Scheduling day {day}: start={start_time} (was {slot.start}), "
                    f"end={end_time} (was {slot.end})"
                )

                start_job = (
                    _get_day_scheduler(day)
                    .at(start_time)
                    .do(lambda: run_in_background(self._planned_restart_bot_task))
                )
                self._scheduled_jobs.append(start_job)

                end_job = (
                    _get_day_scheduler((day + 1) % 7 if start_time > end_time else day)
                    .at(end_time)
                    .do(lambda: run_in_background(self._planned_stop_bot_task))
                )
                self._scheduled_jobs.append(end_job)

        midnight_job = (
            schedule.every().day.at("00:00").do(lambda: self._reschedule_with_new_random_times(profile_id))
        )
        self._scheduled_jobs.append(midnight_job)

    def _reschedule_with_new_random_times(self, profile_id: str) -> None:
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

        current_minutes = now.hour * 60 + now.minute
        current_day = now.weekday()
        for slot in self._randomized_slots_by_day.get(current_day, []):
            start, end = _slot_minutes(slot)
            if start <= end and start <= current_minutes <= end:
                return True
            if start > end and current_minutes >= start:
                return True

        previous_day = (current_day - 1) % 7
        for slot in self._randomized_slots_by_day.get(previous_day, []):
            start, end = _slot_minutes(slot)
            if start > end and current_minutes <= end:
                return True
        return False

    def stop_scheduled_runtime(self) -> None:
        self.logger.info("Stopping bot")
        if self._is_kamas_mule_profile:
            if KamasMuleRegistry().close_window(self.account.apikey.login):
                self.logger.info("Waiting for the active kamas mule reservation")
                self._schedule_mule_stop_retry()
                return
        runtime_is_active = (
            self.is_playing_event.is_set()
            or self.event_manager.request_disconnect_callback is not None
            or self.process_manager.is_bot_process_running()
        )
        if runtime_is_active:
            self._disconnect_runtime()
        else:
            self.logger.info("Bot runtime is already stopped")

    def _disconnect_runtime(self) -> None:
        if self._is_kamas_mule_profile:
            KamasMuleRegistry().mark_unavailable(self.account.apikey.login)
        self.behavior_coordinator.stop_behaviors()
        self.bot_signals.stop.emit()

        request_disconnect = self.event_manager.request_disconnect_callback
        if self.event_manager.is_socket_mode:
            assert request_disconnect is not None, "Socket mode must define a request_disconnect_callback"
        if request_disconnect is not None:
            request_disconnect()

        self.process_manager.kill_process()

    def _manual_disconnect_bot(self) -> None:
        self.logger.info("Disconnecting bot")
        self._disconnect_runtime()

    def _planned_restart_bot(self) -> None:
        self.logger.info("Restarting bot")
        if not self.is_in_randomized_playtime(datetime.now()):
            return self.logger.info("Bot is not anymore in playtime")

        if not self.is_playing_event.is_set():
            self.bot_signals.play.emit(False)
            self.shared_signals.launch_account.emit(self.account.apikey.login)
        else:
            self.logger.info("Bot is playing, dont restart")

    def _planned_stop_bot_task(self, _progress_callback: Callable[[str], None]) -> None:
        self.stop_scheduled_runtime()

    def _manual_disconnect_bot_task(self, _progress_callback: Callable[[str], None]) -> None:
        self._manual_disconnect_bot()

    def _planned_restart_bot_task(self, _progress_callback: Callable[[str], None]) -> None:
        self._planned_restart_bot()

    def _schedule_mule_stop_retry(self) -> None:
        if self._pending_mule_stop is not None:
            self._pending_mule_stop.cancel()
        self._pending_mule_stop = threading.Timer(5, lambda: run_in_background(self._planned_stop_bot_task))
        self._pending_mule_stop.start()


def run_continuously(interval: int = 1) -> threading.Event:
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        def run(self) -> None:
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def _add_random_minutes(
    time_str: str,
    random_minutes_min: int = SCHEDULE_RANDOM_MINUTES_MIN,
    random_minutes_max: int = SCHEDULE_RANDOM_MINUTES_MAX,
) -> str:
    """Add random minutes to a time string (delays start, eats into playtime)."""
    hours, minutes = map(int, time_str.split(":"))
    random_minutes = random.randint(random_minutes_min, random_minutes_max)
    total_minutes = hours * 60 + minutes + random_minutes
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60
    return f"{new_hours:02d}:{new_minutes:02d}"


def _subtract_random_minutes(
    time_str: str,
    random_minutes_min: int = SCHEDULE_RANDOM_MINUTES_MIN,
    random_minutes_max: int = SCHEDULE_RANDOM_MINUTES_MAX,
) -> str:
    """Subtract random minutes from a time string (stops earlier, eats into playtime)."""
    hours, minutes = map(int, time_str.split(":"))
    random_minutes = random.randint(random_minutes_min, random_minutes_max)
    total_minutes = hours * 60 + minutes - random_minutes
    if total_minutes < 0:
        total_minutes += 24 * 60
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60
    return f"{new_hours:02d}:{new_minutes:02d}"


def _get_day_scheduler(day: int) -> schedule.Job:
    match day:
        case 0:
            return schedule.every().monday
        case 1:
            return schedule.every().tuesday
        case 2:
            return schedule.every().wednesday
        case 3:
            return schedule.every().thursday
        case 4:
            return schedule.every().friday
        case 5:
            return schedule.every().saturday
        case 6:
            return schedule.every().sunday
        case _:
            raise ValueError(f"Unknown day index: {day}")


def _slot_minutes(slot: RandomizedSlot) -> tuple[int, int]:
    start_hour, start_minute = map(int, slot.start.split(":"))
    end_hour, end_minute = map(int, slot.end.split(":"))
    return start_hour * 60 + start_minute, end_hour * 60 + end_minute
