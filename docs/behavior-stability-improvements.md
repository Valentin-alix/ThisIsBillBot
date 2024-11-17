# Behavior Stability Improvements

**Date**: 2025-12-30
**Status**: Proposal - Not yet implemented
**Context**: Analysis of instability issues in the behavior lifecycle management system

## Executive Summary

The current behavior architecture suffers from **silent failures** and **race conditions** that make debugging extremely difficult. This document proposes a phased approach to improve stability through fail-fast error handling, explicit state machines, and better observability.

## Current Problems

### 1. Silent Failures Mask Real Bugs

**Location**: [behavior.py:72-74](../src/core/behaviors/behavior.py#L72-L74)

```python
if not self.is_running.is_set():
    self.logger.warning("Already stopped, returning early")
    return
```

**Problem**: Warnings on invalid states hide bugs that should be impossible:
- Double `stop()` calls indicate coordination bugs
- Starting an already-running behavior suggests race conditions
- Parent not running when starting child violates lifecycle contracts

**Impact**: Bugs propagate silently, manifesting as seemingly unrelated failures later.

### 2. Race Conditions on `is_running` Event

**Location**: [behavior.py:64-65](../src/core/behaviors/behavior.py#L64-L65)

```python
if not self.is_running.is_set():
    return
```

**Problem**: Check-then-act pattern without atomic lock:
1. Thread A checks `is_running` → True
2. Thread B calls `stop()`, sets `is_running` → False
3. Thread A proceeds thinking behavior is still running

**Impact**: Callbacks execute after behavior stopped, timers fire on dead behaviors.

### 3. Ambiguous Lifecycle Management

**Issues**:
- Behavior can be `start()`ed while already running → silently restarts ([behavior.py:38-40](../src/core/behaviors/behavior.py#L38-L40))
- Callbacks may fire after `stop()` via pending timers ([behavior.py:63-67](../src/core/behaviors/behavior.py#L63-L67))
- Children can outlive parents if stop synchronization fails
- No clear distinction between "stopping" and "stopped" states

**Impact**: Unpredictable behavior lifecycle, hard-to-reproduce bugs.

### 4. Lock Granularity Issues

**Observations**:
- `event_manager.lock` used for both state mutations AND network operations
- Long-running operations inside lock can cause contention
- Nested lock acquisition patterns risk deadlocks

**Example**: [behavior.py:66-67](../src/core/behaviors/behavior.py#L66-L67)
```python
with self.event_manager.lock:
    func()  # Unknown duration, may acquire other locks
```

## Proposed Solutions

### Phase 1: Fail-Fast with Strict Exceptions ⚡

**Objective**: Replace all silent warnings with explicit exceptions to surface bugs immediately.

**Changes**:

1. Create custom exception class:
```python
class BehaviorLifecycleError(Exception):
    """Raised when behavior lifecycle contracts are violated"""
    pass
```

2. Replace warnings with exceptions in `behavior.py`:

```python
def stop(self) -> None:
    with self.event_manager.lock:
        if not self.is_running.is_set():
            raise BehaviorLifecycleError(
                f"{self.__class__.__name__} double-stop detected. "
                f"This indicates a bug in behavior coordination logic. "
                f"Stack trace will show where the duplicate stop originated."
            )
        self.logger.info("Stopping")
        self.is_running.clear()
        self.clear_behavior()
        if self.parent and self in self.parent.children:
            self.parent.children.remove(self)

def start(self, callback, parent, *args, **kwargs) -> None:
    with self.event_manager.lock:
        if parent and not parent.is_running.is_set():
            raise BehaviorLifecycleError(
                f"Cannot start {self.__class__.__name__}: "
                f"parent {parent.__class__.__name__} is not running. "
                f"Parent may have been stopped prematurely."
            )
        if self.is_running.is_set():
            raise BehaviorLifecycleError(
                f"{self.__class__.__name__} is already running. "
                f"Call stop() explicitly before restarting, or check coordination logic."
            )

        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.is_running.set()
        self.callback = callback
        self.run(*args, **kwargs)
```

**Benefits**:
- Immediate detection of lifecycle bugs with precise stack traces
- Forces fixes rather than masking issues
- No silent state corruption

**Risks**:
- Will expose existing bugs (crashes initially)
- Requires fixing coordination logic in behaviors

**Estimated Impact**: High bug discovery rate in first week, then stable.

---

### Phase 2: Explicit State Machine 🔧

**Objective**: Replace boolean `is_running` Event with a proper state machine to prevent invalid transitions.

**Design**:

```python
from enum import Enum, auto
from threading import Lock

class BehaviorState(Enum):
    """Explicit behavior lifecycle states"""
    IDLE = auto()       # Initial state, never started
    STARTING = auto()   # start() called, running setup
    RUNNING = auto()    # run() executing, fully operational
    STOPPING = auto()   # stop() called, cleanup in progress
    STOPPED = auto()    # Fully stopped, can be restarted
    FAILED = auto()     # Exception during execution

class BehaviorStateError(Exception):
    """Raised when invalid state transition is attempted"""
    pass

@dataclass
class Behavior(ABC, ContextualLogger):
    # ... existing fields ...

    _state: BehaviorState = field(init=False, default=BehaviorState.IDLE)
    _state_lock: Lock = field(init=False, default_factory=Lock)

    def _transition(
        self,
        from_states: set[BehaviorState],
        to_state: BehaviorState,
        reason: str = ""
    ) -> None:
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
                raise BehaviorStateError(
                    f"{self.__class__.__name__} invalid transition: "
                    f"{self._state.name} -> {to_state.name}. "
                    f"Expected current state in {[s.name for s in from_states]}. "
                    f"Reason: {reason}"
                )
            old_state = self._state
            self._state = to_state
            self.logger.debug(
                f"State transition: {old_state.name} -> {to_state.name}" +
                (f" ({reason})" if reason else "")
            )

    @property
    def is_running(self) -> Event:
        """Backward compatibility - returns Event that reflects RUNNING state"""
        with self._state_lock:
            event = Event()
            if self._state == BehaviorState.RUNNING:
                event.set()
            return event

    @property
    def state(self) -> BehaviorState:
        """Thread-safe state accessor"""
        with self._state_lock:
            return self._state

    def start(self, callback, parent, *args, **kwargs) -> None:
        # Validate transition before acquiring event_manager lock
        self._transition(
            {BehaviorState.IDLE, BehaviorState.STOPPED},
            BehaviorState.STARTING,
            reason=f"start() called with parent={parent.__class__.__name__ if parent else None}"
        )

        with self.event_manager.lock:
            if parent and parent.state != BehaviorState.RUNNING:
                self._transition({BehaviorState.STARTING}, BehaviorState.IDLE)
                raise BehaviorLifecycleError(
                    f"Parent {parent.__class__.__name__} in state {parent.state.name}, "
                    f"expected RUNNING"
                )

            self.parent = parent
            if self.parent:
                self.parent.children.append(self)
            self.callback = callback

            self._transition(
                {BehaviorState.STARTING},
                BehaviorState.RUNNING,
                reason="setup complete, entering run()"
            )

            try:
                self.run(*args, **kwargs)
            except Exception as e:
                self._transition(
                    {BehaviorState.RUNNING},
                    BehaviorState.FAILED,
                    reason=f"Exception in run(): {e}"
                )
                raise

    def stop(self) -> None:
        self._transition(
            {BehaviorState.RUNNING, BehaviorState.FAILED},
            BehaviorState.STOPPING,
            reason="stop() called"
        )

        with self.event_manager.lock:
            self.logger.info("Stopping")
            self.clear_behavior()
            if self.parent and self in self.parent.children:
                self.parent.children.remove(self)

        self._transition(
            {BehaviorState.STOPPING},
            BehaviorState.STOPPED,
            reason="cleanup complete"
        )
```

**Valid Transition Table**:

| From      | To        | Trigger                  | Validation                       |
|-----------|-----------|--------------------------|----------------------------------|
| IDLE      | STARTING  | `start()` called         | Parent must be RUNNING or None   |
| STARTING  | RUNNING   | Setup complete           | Automatic after `run()` invoked  |
| STARTING  | IDLE      | Parent validation failed | Rollback on error                |
| RUNNING   | STOPPING  | `stop()` called          | Always valid                     |
| RUNNING   | FAILED    | Exception in `run()`     | Automatic on exception           |
| FAILED    | STOPPING  | `stop()` called          | Cleanup after failure            |
| STOPPING  | STOPPED   | Cleanup complete         | Automatic after `clear_behavior()`|
| STOPPED   | STARTING  | `start()` called again   | Restart allowed                  |

**Benefits**:
- Invalid transitions impossible by construction
- Clear intermediate states prevent race conditions
- Debuggable state history
- Backward compatible via `is_running` property

**Migration Strategy**:
1. Add state machine alongside existing `is_running` Event
2. Keep `is_running.is_set()` working via property
3. Gradually migrate behaviors to use `.state` instead
4. Remove Event-based `is_running` once all behaviors migrated

---

### Phase 3: Async Guards and Timer Safety 🛡️

**Objective**: Prevent callbacks and timers from executing after behavior stops.

**Changes**:

1. **Guarded timer execution**:

```python
def run_timer(self, range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
    if isinstance(range_time, tuple):
        wait_time = get_random_range(range_time)
    else:
        wait_time = range_time

    def guarded_func():
        # Check state WITHOUT acquiring event_manager lock first
        with self._state_lock:
            if self._state != BehaviorState.RUNNING:
                self.logger.debug(
                    f"Timer fired but behavior in state {self._state.name}, ignoring execution"
                )
                return

        # Only acquire heavy lock if we're actually running
        with self.event_manager.lock:
            # Double-check after acquiring lock (state may have changed)
            with self._state_lock:
                if self._state != BehaviorState.RUNNING:
                    return
            func()

    timer = Timer(wait_time, guarded_func)
    self.timers.append(timer)
    timer.start()
```

2. **Protected finish() against double-callback**:

```python
def finish(self, error_code: str | None = None, *args, **kwargs) -> None:
    # Extract callback atomically before stop()
    with self._state_lock:
        if self._state not in {BehaviorState.RUNNING, BehaviorState.FAILED}:
            self.logger.warning(
                f"finish() called in state {self._state.name}, "
                f"ignoring to prevent double-callback"
            )
            return

        # Atomically extract and clear callback to prevent double-call
        callback = self.callback
        self.callback = None

    if error_code is not None:
        self.logger.warning(f"Finished with error: {error_code}")

    self.stop()

    # Call callback AFTER stop completes, outside all locks
    if callback:
        try:
            callback(error_code, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Exception in finish callback: {e}", exc_info=True)
```

3. **Timeout mechanism for stuck behaviors**:

```python
@dataclass
class Behavior(ABC, ContextualLogger):
    # ... existing fields ...
    _timeout_timer: Timer | None = field(init=False, default=None)
    _max_execution_time: float = field(init=False, default=300.0)  # 5 minutes

    def start(self, callback, parent, *args, **kwargs) -> None:
        # ... existing start logic ...

        # Start watchdog timer
        self._timeout_timer = Timer(
            self._max_execution_time,
            lambda: self._on_timeout()
        )
        self._timeout_timer.start()

    def _on_timeout(self) -> None:
        """Called when behavior exceeds max execution time"""
        with self._state_lock:
            if self._state != BehaviorState.RUNNING:
                return  # Already stopped, ignore

        self.logger.error(
            f"{self.__class__.__name__} exceeded max execution time "
            f"({self._max_execution_time}s), forcing stop"
        )
        self.finish(error_code="TIMEOUT")

    def stop(self) -> None:
        # Cancel timeout timer
        if self._timeout_timer:
            self._timeout_timer.cancel()
            self._timeout_timer = None

        # ... existing stop logic ...
```

**Benefits**:
- Timers can't fire on stopped behaviors
- Double-callback impossible
- Automatic cleanup for hung behaviors
- Better lock hygiene (check state before heavy lock)

---

### Phase 4: Enhanced Observability 📊

**Objective**: Add comprehensive logging and metrics for debugging lifecycle issues.

**Implementation**:

```python
from dataclasses import dataclass, field
from time import time
from typing import Any

@dataclass
class LifecycleEvent:
    """Record of a behavior lifecycle event"""
    timestamp: float
    state_from: BehaviorState | None
    state_to: BehaviorState
    event_type: str  # "transition", "timer_fired", "callback_invoked", etc.
    details: dict[str, Any]

@dataclass
class Behavior(ABC, ContextualLogger):
    # ... existing fields ...

    _start_timestamp: float | None = field(init=False, default=None)
    _lifecycle_events: list[LifecycleEvent] = field(init=False, default_factory=list)
    _metrics: dict[str, Any] = field(init=False, default_factory=dict)

    def _log_lifecycle_event(
        self,
        event_type: str,
        state_from: BehaviorState | None = None,
        state_to: BehaviorState | None = None,
        **details
    ) -> None:
        """Record a lifecycle event for debugging"""
        now = time()

        event = LifecycleEvent(
            timestamp=now,
            state_from=state_from,
            state_to=state_to or self._state,
            event_type=event_type,
            details=details
        )
        self._lifecycle_events.append(event)

        uptime = now - (self._start_timestamp or now)
        self.logger.debug(
            f"[{self.__class__.__name__}] {event_type} "
            f"{state_from.name if state_from else '?'} -> {event.state_to.name} "
            f"(uptime={uptime:.2f}s) {details}"
        )

    def _transition(self, from_states, to_state, reason=""):
        old_state = self._state
        # ... existing transition logic ...
        self._log_lifecycle_event(
            "state_transition",
            state_from=old_state,
            state_to=to_state,
            reason=reason
        )

    def start(self, callback, parent, *args, **kwargs):
        self._start_timestamp = time()
        self._metrics["start_count"] = self._metrics.get("start_count", 0) + 1
        self._log_lifecycle_event("start", parent=parent.__class__.__name__ if parent else None)
        # ... existing start logic ...

    def stop(self):
        duration = time() - (self._start_timestamp or time())
        self._metrics["total_duration"] = self._metrics.get("total_duration", 0) + duration
        self._log_lifecycle_event("stop", duration=duration)
        # ... existing stop logic ...

    def run_timer(self, range_time, func):
        timer_id = id(func)
        self._log_lifecycle_event("timer_scheduled", timer_id=timer_id, delay=range_time)

        def guarded_func():
            self._log_lifecycle_event("timer_fired", timer_id=timer_id)
            # ... existing guarded logic ...

        # ... rest of run_timer ...

    def get_lifecycle_summary(self) -> str:
        """Generate human-readable lifecycle summary for debugging"""
        lines = [f"\n=== Lifecycle Summary: {self.__class__.__name__} ==="]
        lines.append(f"Current State: {self._state.name}")
        lines.append(f"Metrics: {self._metrics}")
        lines.append("\nEvent History:")

        for event in self._lifecycle_events[-20:]:  # Last 20 events
            relative_time = event.timestamp - (self._start_timestamp or event.timestamp)
            lines.append(
                f"  [{relative_time:6.2f}s] {event.event_type}: "
                f"{event.state_from.name if event.state_from else '?'} -> {event.state_to.name} "
                f"{event.details}"
            )

        return "\n".join(lines)

    def __del__(self):
        """Log lifecycle summary on garbage collection if debugging enabled"""
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(self.get_lifecycle_summary())
```

**Usage for debugging**:

```python
# In any behavior when investigating issues:
try:
    self.some_behavior.start(callback, parent)
except BehaviorLifecycleError as e:
    self.logger.error(f"Lifecycle error: {e}")
    self.logger.error(self.some_behavior.get_lifecycle_summary())
    raise
```

**Benefits**:
- Complete audit trail of behavior execution
- Post-mortem debugging capabilities
- Performance metrics (duration, restart count)
- Easy to export to monitoring systems

---

## Implementation Roadmap

### Week 1: Fail-Fast Foundation
- [ ] Create `BehaviorLifecycleError` exception class
- [ ] Replace all warnings with exceptions in `behavior.py`
- [ ] Update `BehaviorCoordinator.stop_behaviors()` to handle exceptions gracefully
- [ ] Run full test suite, document all crashes
- [ ] Fix revealed coordination bugs one by one
- [ ] Update documentation with new error semantics

**Success Criteria**: All tests pass, no silent failures in logs.

### Week 2: State Machine Migration
- [ ] Implement `BehaviorState` enum and `_transition()` method
- [ ] Add backward-compatible `is_running` property
- [ ] Migrate `start()` and `stop()` to use state machine
- [ ] Add state transition logging
- [ ] Update unit tests to verify state transitions
- [ ] Gradually migrate behaviors from `is_running.is_set()` to `.state`

**Success Criteria**: All behaviors use state machine, no `is_running` Event usage remains.

### Week 3: Async Guards
- [ ] Implement guarded `run_timer()`
- [ ] Add double-callback protection to `finish()`
- [ ] Implement timeout watchdog mechanism
- [ ] Add configuration for per-behavior timeout limits
- [ ] Test timer safety under concurrent stop conditions

**Success Criteria**: No timer callbacks fire after stop, no double-callbacks observed.

### Week 4: Observability
- [ ] Implement `LifecycleEvent` dataclass
- [ ] Add `_log_lifecycle_event()` to all lifecycle methods
- [ ] Create `get_lifecycle_summary()` debug utility
- [ ] Add metrics collection (duration, restarts)
- [ ] Create dashboard visualization for behavior states (optional)
- [ ] Document debugging workflow using lifecycle logs

**Success Criteria**: Can diagnose any lifecycle issue from logs alone.

---

## Testing Strategy

### Unit Tests

Create `tests/test_behaviors/test_behavior_lifecycle.py`:

```python
import unittest
from threading import Event
from unittest.mock import Mock

from src.core.behaviors.behavior import Behavior, BehaviorLifecycleError, BehaviorState

class DummyBehavior(Behavior):
    def run(self):
        pass

class TestBehaviorLifecycle(unittest.TestCase):
    def setUp(self):
        self.event_manager = Mock()
        self.event_manager.lock = Mock()
        self.game_state = Mock()
        self.behavior = DummyBehavior(self.event_manager, self.game_state)

    def test_double_stop_raises_error(self):
        """Phase 1: Verify double stop raises exception"""
        self.behavior.start(callback=None, parent=None)
        self.behavior.stop()

        with self.assertRaises(BehaviorLifecycleError) as ctx:
            self.behavior.stop()

        self.assertIn("double-stop", str(ctx.exception).lower())

    def test_start_when_running_raises_error(self):
        """Phase 1: Verify starting running behavior raises exception"""
        self.behavior.start(callback=None, parent=None)

        with self.assertRaises(BehaviorLifecycleError):
            self.behavior.start(callback=None, parent=None)

    def test_state_transitions_valid(self):
        """Phase 2: Verify state machine transitions"""
        self.assertEqual(self.behavior.state, BehaviorState.IDLE)

        self.behavior.start(callback=None, parent=None)
        self.assertEqual(self.behavior.state, BehaviorState.RUNNING)

        self.behavior.stop()
        self.assertEqual(self.behavior.state, BehaviorState.STOPPED)

    def test_timer_ignores_after_stop(self):
        """Phase 3: Verify timers don't fire after stop"""
        callback_invoked = Event()

        def timer_func():
            callback_invoked.set()

        self.behavior.start(callback=None, parent=None)
        self.behavior.run_timer(0.1, timer_func)
        self.behavior.stop()

        time.sleep(0.2)  # Wait for timer
        self.assertFalse(callback_invoked.is_set())
```

### Integration Tests

Test real behavior coordination scenarios:

```python
def test_parent_child_lifecycle(self):
    """Verify child stops when parent stops"""
    parent = DummyBehavior(self.event_manager, self.game_state)
    child = DummyBehavior(self.event_manager, self.game_state)

    parent.start(callback=None, parent=None)
    child.start(callback=None, parent=parent)

    self.assertEqual(parent.state, BehaviorState.RUNNING)
    self.assertEqual(child.state, BehaviorState.RUNNING)

    parent.stop()

    self.assertEqual(parent.state, BehaviorState.STOPPED)
    self.assertEqual(child.state, BehaviorState.STOPPED)
```

---

## Migration Checklist for Existing Behaviors

When migrating a behavior to the new system:

- [ ] Remove any manual `is_running.is_set()` checks before `finish()` or `stop()`
- [ ] Replace `is_running.is_set()` with `self.state == BehaviorState.RUNNING`
- [ ] Ensure all error paths call `finish(error_code)` instead of bare `stop()`
- [ ] Verify no timers or callbacks can execute after `stop()`
- [ ] Add timeout configuration if behavior can hang
- [ ] Test parent-child coordination if applicable
- [ ] Verify exception handling doesn't swallow `BehaviorLifecycleError`

---

## Performance Considerations

### Lock Contention

**Current Issue**: `event_manager.lock` used for both state and network operations causes contention.

**Solution**: Use separate `_state_lock` for behavior state transitions:
- `_state_lock`: Protects only `_state`, `_lifecycle_events` (fast)
- `event_manager.lock`: Used only when modifying event listeners or sending messages (slow)

**Pattern**:
```python
# Good: Check state with lightweight lock
with self._state_lock:
    if self._state != BehaviorState.RUNNING:
        return

# Then acquire heavy lock only if needed
with self.event_manager.lock:
    # Double-check under heavy lock
    with self._state_lock:
        if self._state != BehaviorState.RUNNING:
            return
    self.event_manager.send(message)
```

### Memory Overhead

**Concern**: `_lifecycle_events` list grows unbounded.

**Solution**: Use bounded deque:
```python
from collections import deque

_lifecycle_events: deque[LifecycleEvent] = field(
    init=False,
    default_factory=lambda: deque(maxlen=100)  # Keep last 100 events
)
```

---

## Rollback Plan

If any phase causes critical issues:

1. **Phase 1 rollback**: Revert exceptions to warnings, add TODO comments
2. **Phase 2 rollback**: Keep state machine, make `is_running` Event primary again
3. **Phase 3 rollback**: Remove timeout watchdog, keep guarded timers
4. **Phase 4 rollback**: Disable lifecycle logging via config flag

**Feature flag approach**:
```python
ENABLE_STRICT_LIFECYCLE = os.getenv("BOT_STRICT_LIFECYCLE", "true").lower() == "true"

if ENABLE_STRICT_LIFECYCLE:
    raise BehaviorLifecycleError(...)
else:
    self.logger.warning(...)
```

---

## References

- Current implementation: [src/core/behaviors/behavior.py](../src/core/behaviors/behavior.py)
- Coordinator logic: [src/core/bot/execution/behavior_coordinator.py](../src/core/bot/execution/behavior_coordinator.py)
- Related: [docs/listener-cleanup-proposal.md](./listener-cleanup-proposal.md)

## Related Issues

Document known bugs that this proposal addresses:
- Double-stop warnings in harvester behavior
- Race conditions in attacker behavior timing
- Parent-child coordination failures in multi-farming
- Hung behaviors requiring manual restart

---

**Next Steps**: Review this proposal, prioritize phases, and begin Phase 1 implementation.
