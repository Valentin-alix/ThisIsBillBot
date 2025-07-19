from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from threading import RLock, Timer
from typing import ParamSpec, Protocol, overload

from google.protobuf.message import Message

from src.core.events_manager.event_manager import EventManager
from src.core.states.game_state import GameState
from src.exceptions import UnhandledErrorCodeException
from src.services.human_timings import get_random_range
from src.services.logging_utils.contextual_logger import ContextualLogger


class BehaviorLifecycleError(Exception):
    """Raised when behavior lifecycle contracts are violated"""

    pass


class BehaviorStateError(Exception):
    """Raised when invalid state transition is attempted"""

    pass


class BehaviorState(Enum):
    """Explicit behavior lifecycle states"""

    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()


RunParams = ParamSpec("RunParams")


class RunnableBehavior(Protocol[RunParams]):
    def run(self, *args: RunParams.args, **kwargs: RunParams.kwargs) -> None: ...


@dataclass
class Behavior(ContextualLogger):
    event_manager: EventManager
    game_state: GameState
    callback: Callable[..., None] | None = field(init=False, default=None)
    parent: "Behavior|None" = field(init=False, default=None)

    _state: BehaviorState = field(init=False, default=BehaviorState.STOPPED)
    _state_lock: RLock = field(init=False, default_factory=RLock)
    children: list["Behavior"] = field(init=False, default_factory=list["Behavior"])
    timers: list[Timer] = field(init=False, default_factory=list[Timer])

    def _transition(
        self, from_states: set[BehaviorState], to_state: BehaviorState, reason: str = ""
    ) -> bool:
        """
        Atomic state transition with validation.

        Args:
            from_states: Valid source states for this transition
            to_state: Target state
            reason: Optional debug message

        Raises:
            BehaviorStateError: If current state not in from_states
        """
        with self._state_lock:
            if self._state not in from_states:
                error = (
                    f"{self.__class__.__name__} invalid transition: "
                    f"{self._state.name} -> {to_state.name}. "
                    f"Expected current state in {[s.name for s in from_states]}. "
                    f"Reason: {reason}"
                )
                self.logger.error(error)
                return False

            old_state = self._state
            self._state = to_state
            self.logger.debug(
                f"State transition: {old_state.name} -> {to_state.name}"
                + (f" ({reason})" if reason else "")
            )
            self._record_behavior_event(
                "transition",
                from_state=old_state.name,
                to_state=to_state.name,
                reason=reason,
            )
            return True

    @property
    def state(self) -> BehaviorState:
        """Thread-safe state accessor"""
        with self._state_lock:
            return self._state

    @overload
    def start(
        self: RunnableBehavior[RunParams],
        callback: Callable[..., None] | None,
        parent: "Behavior|None",
        *args: RunParams.args,
        **kwargs: RunParams.kwargs,
    ) -> None: ...

    @overload
    def start(
        self: RunnableBehavior[RunParams],
        callback: Callable[..., None] | None,
        parent: "Behavior|None",
        *args: RunParams.args,
        **kwargs: RunParams.kwargs,
    ) -> None: ...

    def start(
        self,
        callback: Callable[..., None] | None,
        parent: "Behavior|None",
        *args: object,
        **kwargs: object,
    ) -> None:
        if not self._transition(
            {BehaviorState.STOPPED},
            BehaviorState.STARTING,
            reason=f"start() called with parent={parent.__class__.__name__ if parent else None}",
        ):
            return

        with self.event_manager.lock:
            if parent and parent.state != BehaviorState.RUNNING:
                error = (
                    f"Cannot start {self.__class__.__name__}: "
                    f"parent {parent.__class__.__name__} in state {parent.state.name}, "
                    f"expected RUNNING"
                )
                self.logger.error(error)
                return

            self.parent = parent
            if self.parent:
                self.parent.children.append(self)
            self.callback = callback

            if not self._transition(
                {BehaviorState.STARTING},
                BehaviorState.RUNNING,
                reason="setup complete, entering run()",
            ):
                return

        self.logger.debug(f"Starting {self.__class__.__name__}")
        if self.parent is None:
            self._record_state_snapshot(f"{self.__class__.__name__}.start")
        run_method = getattr(self, "run", None)
        if not callable(run_method):
            raise TypeError(f"{self.__class__.__name__} must define a run() method")
        run_method(*args, **kwargs)

    def send_message_delayed(
        self, message: Message, delay: tuple[float, float] | float
    ) -> None:
        self.run_timer(delay, lambda: self.event_manager.send(message))

    def run_timer(
        self, range_time: tuple[float, float] | float, func: Callable[[], None]
    ) -> None:
        if isinstance(range_time, tuple):
            wait_time = get_random_range(range_time)
        else:
            wait_time = range_time
        timer = Timer(wait_time, lambda: self.run_timed_func(func))
        self.timers.append(timer)
        timer.start()

    def run_timed_func(self, func: Callable[[], None]) -> None:
        with self._state_lock:
            if self._state != BehaviorState.RUNNING:
                self.logger.warning(
                    f"Timer fired but behavior in state {self._state.name}, ignoring"
                )
                return
        func()

    def stop(self) -> None:
        with self._state_lock:
            if self._state == BehaviorState.STOPPED:
                error = "Already stopped, ignoring"
                self.logger.debug(error)
                return

            if self._state == BehaviorState.STOPPING:
                error = "Already stopping, ignoring"
                self.logger.debug(error)
                return

        self._transition(
            {BehaviorState.RUNNING, BehaviorState.STARTING},
            BehaviorState.STOPPING,
            reason="stop() called",
        )

        with self.event_manager.lock:
            self.logger.info("Stopping")
            self.clear_behavior()
            if self.parent and self in self.parent.children:
                self.parent.children.remove(self)

        self._transition(
            {BehaviorState.STOPPING}, BehaviorState.STOPPED, reason="cleanup complete"
        )

    def force_reset(self) -> None:
        """
        Force reset behavior to STOPPED state without validation.
        Used for recovery when process was killed during execution.
        """
        with self._state_lock:
            self._state = BehaviorState.STOPPED

        with self.event_manager.lock:
            self.clear_behavior()
            self.parent = None
            self.callback = None

    def clear_behavior(self) -> None:
        with self.event_manager.lock:
            for timer in self.timers:
                timer.cancel()
            self.timers.clear()

            self.event_manager.clear_listener_by_origin(self)
            self.event_manager.clear_modifier_by_origin(self)

            while self.children:
                child = self.children.pop()
                child.stop()

    def finish(
        self, error_code: str | None = None, *args: object, **kwargs: object
    ) -> None:
        with self._state_lock:
            if self._state not in {BehaviorState.RUNNING, BehaviorState.STARTING}:
                error = f"finish() called in state {self._state.name}"
                self.logger.error(error)
                return

            callback = self.callback
            self.callback = None

        if error_code is not None:
            self.logger.warning(f"Finished with error: {error_code}")

        self._record_behavior_event("finish", error_code=error_code)
        if self.parent is None:
            self._record_state_snapshot(f"{self.__class__.__name__}.finish")

        self.stop()

        if callback:
            callback(error_code, *args, **kwargs)

    def unregister_listener(self, event_type: type[Message], reason: str = "") -> None:
        """
        Nettoie un listener spécifique en cours d'exécution.

        Note: Utilisez cette méthode uniquement si vous devez nettoyer
        un listener pendant que le behavior continue à s'exécuter.
        Si le behavior va terminer juste après, laissez clear_behavior()
        gérer le nettoyage automatiquement.

        Args:
            event_type: Type d'événement à dé-enregistrer
            reason: Raison du nettoyage manuel (pour debug/doc)
        """
        if reason:
            self.logger.debug(
                f"Manual listener cleanup: {event_type.__name__} - {reason}"
            )
        self.event_manager.clear_listener_by_origin_and_type(event_type, self)

    def raise_if_error(self, error_code: str | None) -> None:
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

    def behavior_tree_snapshot(self) -> list[str]:
        """Indented snapshot of the running behavior tree, rooted at the
        top-most parent, with ``<-`` marking the current behavior."""
        root = self
        while root.parent is not None:
            root = root.parent

        lines: list[str] = []

        def walk(behavior: "Behavior", depth: int) -> None:
            marker = " <-" if behavior is self else ""
            lines.append(
                "  " * depth
                + f"{behavior.__class__.__name__}[{behavior.state.name}]"
                + marker
            )
            for child in list(behavior.children):
                walk(child, depth + 1)

        walk(root, 0)
        return lines

    def _record_behavior_event(
        self,
        event: str,
        from_state: str | None = None,
        to_state: str | None = None,
        error_code: str | None = None,
        reason: str = "",
    ) -> None:
        self.event_manager.mark_activity()
        recorder = self.event_manager.debug_recorder
        if recorder is None:
            return
        recorder.record_behavior(
            behavior=self.__class__.__name__,
            event=event,
            tree=self.behavior_tree_snapshot(),
            from_state=from_state,
            to_state=to_state,
            error_code=error_code,
            parent=self.parent.__class__.__name__ if self.parent else None,
            reason=reason,
        )

    def _record_state_snapshot(self, trigger: str) -> None:
        recorder = self.event_manager.debug_recorder
        if recorder is None:
            return
        recorder.record_state(
            trigger=trigger, snapshot=self.game_state.debug_snapshot()
        )
