"""Generic stuck detector.

A per-bot daemon thread that flags when a top-level action behavior keeps
running while the bot logic stops making progress (no behavior transition for
``threshold_s``). On a trip it dumps the full context (running behavior tree,
game state snapshot, registered listeners with their age, last message) into
the debug recorder so an agent can pinpoint the infinite wait.

"Progress" is defined as a behavior transition (see
``EventManager.mark_activity``): a truly stuck bot is waiting for a message
that never comes and therefore never transitions.
"""

import threading
import time
from dataclasses import dataclass, field
from threading import Event
from typing import Callable

from src.core.behaviors.behavior import Behavior, BehaviorState
from src.core.behaviors.idle_behavior import IdleBehavior
from src.core.events_manager.event_manager import EventManager
from src.core.states.game_state import GameState
from src.services.logging_utils.contextual_logger import ContextualLogger

_DEFAULT_THRESHOLD_S = 90.0
_DEFAULT_TICK_S = 5.0


@dataclass
class StuckWatchdog(ContextualLogger):
    event_manager: EventManager
    game_state: GameState
    is_playing_event: Event
    get_running_top_level_behaviors: Callable[[], list[Behavior]]
    threshold_s: float = _DEFAULT_THRESHOLD_S
    tick_s: float = _DEFAULT_TICK_S

    _stop_event: Event = field(init=False, default_factory=Event)
    _thread: threading.Thread = field(init=False)
    _last_reported_activity: float = field(init=False, default=-1.0)

    def __post_init__(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run(self) -> None:
        while not self._stop_event.wait(self.tick_s):
            self._check()

    def _check(self) -> None:
        if not self.is_playing_event.is_set():
            return
        running = self.get_running_top_level_behaviors()
        if not running:
            return
        if all(self._is_intentionally_idle(behavior) for behavior in running):
            return

        last_activity = self.event_manager.last_activity_monotonic
        idle_s = time.monotonic() - last_activity
        if idle_s < self.threshold_s:
            return
        if last_activity == self._last_reported_activity:
            return

        self._last_reported_activity = last_activity
        self._report(running[0], idle_s)

    def _is_intentionally_idle(self, behavior: Behavior) -> bool:
        running_children = [
            child
            for child in list(behavior.children)
            if child.state is BehaviorState.RUNNING
        ]
        if running_children:
            return all(self._is_intentionally_idle(child) for child in running_children)
        return (
            isinstance(behavior, IdleBehavior)
            and behavior.state is BehaviorState.RUNNING
        )

    def _report(self, behavior: Behavior, idle_s: float) -> None:
        reason = (
            f"No bot progress for {idle_s:.0f}s while "
            f"{behavior.__class__.__name__} is running"
        )
        self.logger.warning(f"STUCK: {reason}")

        recorder = self.event_manager.debug_recorder
        if recorder is None:
            return
        recorder.record_stuck(
            reason=reason,
            seconds_since_progress=round(idle_s, 1),
            tree=behavior.behavior_tree_snapshot(),
            snapshot=self.game_state.debug_snapshot(),
            listeners=self.event_manager.listeners_debug_snapshot(),
            last_message=self.event_manager.last_message_name,
        )
