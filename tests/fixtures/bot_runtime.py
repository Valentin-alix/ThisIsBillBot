from dataclasses import dataclass, field
from threading import Event, RLock
from unittest.mock import Mock

from src.core.bot.execution.behavior_coordinator import BehaviorCoordinator
from src.core.bot.lifecycle.scheduler import BotScheduler
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.accounts import make_account


@dataclass
class SignalEmitter:
    emit: Mock = field(default_factory=Mock)


@dataclass
class BotSignalsFake:
    stop: SignalEmitter = field(default_factory=SignalEmitter)
    play: SignalEmitter = field(default_factory=SignalEmitter)
    play_mule_kamas: SignalEmitter = field(default_factory=SignalEmitter)
    play_auto_bot: SignalEmitter = field(default_factory=SignalEmitter)


@dataclass
class SharedSignalsFake:
    launch_account: SignalEmitter = field(default_factory=SignalEmitter)
    bot_removed: SignalEmitter = field(default_factory=SignalEmitter)
    new_bot_added: SignalEmitter = field(default_factory=SignalEmitter)


@dataclass
class EventManagerLockFake:
    lock: RLock = field(default_factory=RLock)


class ScheduleProfileControllerMock:
    def get_profile(self, profile_id: str) -> object | None:
        del profile_id
        return None


def run_in_background_mock(
    func: object,
    on_success: object | None = None,
    on_error: object | None = None,
    on_progress: object | None = None,
    parent: object | None = None,
) -> None:
    del func, on_success, on_error, on_progress, parent


@dataclass
class BotConfigMock:
    schedule_profile: str | None = None


def make_bot_scheduler() -> BotScheduler:
    return BotScheduler(
        _logger=Mock(),
        account=make_account("test-login", 0),
        bot_signals=BotSignalsFake(),  # type: ignore
        shared_signals=SharedSignalsFake(),  # type: ignore
        log_signals=Mock(),
        is_playing_event=Event(),
        msg_info_signals=Mock(),
        get_bot_config=Mock(return_value=None),
        behavior_coordinator=Mock(),
        process_manager=Mock(),
        event_manager=EventManager(_logger=Mock()),
    )


def make_behavior_coordinator() -> BehaviorCoordinator:
    return BehaviorCoordinator(
        _logger=Mock(),
        is_connected_event=Event(),
        is_ready_to_play_event=Event(),
        is_playing_event=Event(),
        from_manual_play=Event(),
        event_manager=EventManagerLockFake(),  # type: ignore
        fight_behavior=Mock(),
        harvester_behavior=Mock(),
        fighter_behavior=Mock(),
        craft_behavior=Mock(),
        mule_accept_kamas_behavior=Mock(),
        auto_bot_behavior=Mock(),
        usable_behaviors=[],
        bot_signals=BotSignalsFake(stop=SignalEmitter()),  # type: ignore
        shared_signals=SharedSignalsFake(),  # type: ignore
        account=make_account("test-login", 0),
        get_bot_config=Mock(return_value=None),
    )
