import time
from dataclasses import dataclass
from threading import Event
from typing import NamedTuple
from unittest.mock import MagicMock

from src.core.behaviors.behavior import Behavior
from src.core.bot.execution.watchdog import StuckWatchdog
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext


@dataclass
class _StubBehavior(Behavior):
    def run(self) -> None: ...


class _WatchdogSetup(NamedTuple):
    watchdog: StuckWatchdog
    event_manager: EventManager
    recorder: MagicMock


def _make_watchdog(
    game_state_ctx: GameStateContext, running: list[Behavior]
) -> _WatchdogSetup:
    recorder = MagicMock()
    event_manager = EventManager(_logger=game_state_ctx.logger, debug_recorder=recorder)
    event_manager.last_message_name = "MapComplementaryInformationEvent"
    is_playing = Event()
    is_playing.set()
    watchdog = StuckWatchdog(
        _logger=game_state_ctx.logger,
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        is_playing_event=is_playing,
        get_running_top_level_behaviors=lambda: running,
        threshold_s=90.0,
        tick_s=1000.0,  # background thread stays dormant during the test
    )
    return _WatchdogSetup(watchdog, event_manager, recorder)


def _stub_behavior(game_state_ctx: GameStateContext) -> _StubBehavior:
    return _StubBehavior(
        _logger=game_state_ctx.logger,
        event_manager=MagicMock(),
        game_state=game_state_ctx.game_state,
    )


def test_watchdog_reports_stuck_with_full_context(
    game_state_ctx: GameStateContext,
) -> None:
    setup = _make_watchdog(game_state_ctx, [_stub_behavior(game_state_ctx)])
    try:
        setup.event_manager.last_activity_monotonic = time.monotonic() - 200.0
        setup.watchdog._check()

        setup.recorder.record_stuck.assert_called_once()
        kwargs = setup.recorder.record_stuck.call_args.kwargs
        assert kwargs["tree"] == ["_StubBehavior[STOPPED] <-"]
        assert kwargs["last_message"] == "MapComplementaryInformationEvent"
        assert kwargs["seconds_since_progress"] >= 90.0
        assert "map_id" in kwargs["snapshot"]
    finally:
        setup.watchdog.stop()


def test_watchdog_reports_once_per_episode(
    game_state_ctx: GameStateContext,
) -> None:
    setup = _make_watchdog(game_state_ctx, [_stub_behavior(game_state_ctx)])
    try:
        setup.event_manager.last_activity_monotonic = time.monotonic() - 200.0
        setup.watchdog._check()
        setup.watchdog._check()
        setup.recorder.record_stuck.assert_called_once()

        # progress resumes (new activity timestamp) then stalls again
        setup.event_manager.last_activity_monotonic = time.monotonic() - 150.0
        setup.watchdog._check()
        assert setup.recorder.record_stuck.call_count == 2
    finally:
        setup.watchdog.stop()


def test_watchdog_silent_when_not_playing(
    game_state_ctx: GameStateContext,
) -> None:
    setup = _make_watchdog(game_state_ctx, [_stub_behavior(game_state_ctx)])
    try:
        setup.watchdog.is_playing_event.clear()
        setup.event_manager.last_activity_monotonic = time.monotonic() - 200.0
        setup.watchdog._check()
        setup.recorder.record_stuck.assert_not_called()
    finally:
        setup.watchdog.stop()


def test_watchdog_silent_when_no_running_behavior(
    game_state_ctx: GameStateContext,
) -> None:
    setup = _make_watchdog(game_state_ctx, [])
    try:
        setup.event_manager.last_activity_monotonic = time.monotonic() - 200.0
        setup.watchdog._check()
        setup.recorder.record_stuck.assert_not_called()
    finally:
        setup.watchdog.stop()
