import unittest
from time import sleep
from unittest.mock import patch

from src.core.behaviors.behavior import (
    Behavior,
    BehaviorLifecycleError,
    BehaviorState,
    BehaviorStateError,
)
from tests.test_behaviors.behavior_test_base import BehaviorTestBase


class DummyBehavior(Behavior):
    """Minimal behavior for testing lifecycle"""

    def run(self):
        pass


class TestBehaviorLifecycle(BehaviorTestBase):
    """Test behavior lifecycle with strict exception enforcement (Phase 1)"""

    @patch("src.core.behaviors.behavior.STRICT_MODE", True)
    def test_double_stop_raises_error(self):
        """Phase 1: Verify double stop raises error (BehaviorStateError in Phase 2)"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        behavior.start(callback=None, parent=None)
        behavior.stop()

        with self.assertRaises(BehaviorStateError) as ctx:
            behavior.stop()

        self.assertIn("already stopped", str(ctx.exception).lower())

    @patch("src.core.behaviors.behavior.STRICT_MODE", True)
    def test_start_when_running_raises_error(self):
        """Phase 1: Verify starting running behavior raises error (BehaviorStateError in Phase 2)"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        behavior.start(callback=None, parent=None)

        with self.assertRaises(BehaviorLifecycleError) as ctx:
            behavior.start(callback=None, parent=None)

        self.assertIn("invalid transition", str(ctx.exception).lower())

    @patch("src.core.behaviors.behavior.STRICT_MODE", True)
    def test_start_with_stopped_parent_raises_error(self):
        """Phase 1: Verify starting child with stopped parent raises BehaviorLifecycleError"""
        parent = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        child = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        parent.start(callback=None, parent=None)
        parent.stop()

        with self.assertRaises(BehaviorLifecycleError) as ctx:
            child.start(callback=None, parent=parent)

        self.assertIn("parent", str(ctx.exception).lower())
        self.assertIn("stopped", str(ctx.exception).lower())

    def test_normal_lifecycle_succeeds(self):
        """Verify normal start -> stop lifecycle works without errors"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        self.assertFalse(behavior.state == BehaviorState.RUNNING)

        behavior.start(callback=None, parent=None)
        self.assertTrue(behavior.state == BehaviorState.RUNNING)

        behavior.stop()
        self.assertFalse(behavior.state == BehaviorState.RUNNING)

    def test_parent_child_hierarchy(self):
        """Verify parent-child relationship works correctly"""
        parent = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        child = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        parent.start(callback=None, parent=None)
        child.start(callback=None, parent=parent)

        self.assertTrue(parent.state == BehaviorState.RUNNING)
        self.assertTrue(child.state == BehaviorState.RUNNING)
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children)

        parent.stop()

        self.assertFalse(parent.state == BehaviorState.RUNNING)
        self.assertFalse(child.state == BehaviorState.RUNNING)

    def test_timer_does_not_fire_after_stop(self):
        """Verify timers don't execute after behavior stops"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        callback_executed = []

        def timer_func():
            callback_executed.append(True)

        behavior.start(callback=None, parent=None)
        behavior.run_timer(0.1, timer_func)
        behavior.stop()

        sleep(0.2)
        self.assertEqual(
            len(callback_executed), 0, "Timer callback should not execute after stop"
        )

    def test_finish_calls_callback(self):
        """Verify finish() calls the callback correctly"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        callback = self.create_callback()

        behavior.start(callback=callback, parent=None)
        behavior.finish(error_code=None)

        self.assertTrue(self.callback_called.is_set())
        self.assertIsNone(self.callback_error_code)
        self.assertFalse(behavior.state == BehaviorState.RUNNING)

    def test_finish_with_error_code(self):
        """Verify finish() with error code works correctly"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        callback = self.create_callback()

        behavior.start(callback=callback, parent=None)
        behavior.finish(error_code="TEST_ERROR")

        self.assertTrue(self.callback_called.is_set())
        self.assertEqual(self.callback_error_code, "TEST_ERROR")
        self.assertFalse(behavior.state == BehaviorState.RUNNING)

    def test_state_machine_transitions(self):
        """Phase 2: Verify state machine transitions are valid"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        self.assertEqual(behavior.state, BehaviorState.STOPPED)

        behavior.start(callback=None, parent=None)
        self.assertEqual(behavior.state, BehaviorState.RUNNING)

        behavior.stop()
        self.assertEqual(behavior.state, BehaviorState.STOPPED)

    @patch("src.core.behaviors.behavior.STRICT_MODE", True)
    def test_invalid_state_transition_raises_error(self):
        """Phase 2: Verify invalid state transitions raise BehaviorStateError"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        self.assertEqual(behavior.state, BehaviorState.STOPPED)

        with self.assertRaises(BehaviorStateError) as ctx:
            behavior.stop()

        self.assertIn("already stopped", str(ctx.exception).lower())

    @patch("src.core.behaviors.behavior.STRICT_MODE", True)
    def test_state_machine_prevents_double_start(self):
        """Phase 2: Verify state machine prevents starting already running behavior"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        behavior.start(callback=None, parent=None)
        self.assertEqual(behavior.state, BehaviorState.RUNNING)

        with self.assertRaises(BehaviorLifecycleError) as ctx:
            behavior.start(callback=None, parent=None)

        self.assertIn("invalid transition", str(ctx.exception).lower())

    def test_restart_after_stopped(self):
        """Phase 2: Verify behavior can restart after being stopped"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        behavior.start(callback=None, parent=None)
        self.assertEqual(behavior.state, BehaviorState.RUNNING)

        behavior.stop()
        self.assertEqual(behavior.state, BehaviorState.STOPPED)

        behavior.start(callback=None, parent=None)
        self.assertEqual(behavior.state, BehaviorState.RUNNING)

        behavior.stop()
        self.assertEqual(behavior.state, BehaviorState.STOPPED)

    def test_timer_double_check_prevents_execution(self):
        """Phase 3: Verify timer uses double-check pattern to prevent race conditions"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        callback_executed = []

        def timer_func():
            callback_executed.append(True)

        behavior.start(callback=None, parent=None)
        behavior.run_timer(0.05, timer_func)

        sleep(0.02)
        behavior.stop()

        sleep(0.1)
        self.assertEqual(len(callback_executed), 0, "Timer callback should not execute after stop")

    @patch("src.core.behaviors.behavior.STRICT_MODE", True)
    def test_finish_prevents_double_callback(self):
        """Phase 3: Verify finish() prevents double-callback execution"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        callback_count = []

        def test_callback(error_code):
            callback_count.append(1)

        behavior.start(callback=test_callback, parent=None)
        behavior.finish(error_code=None)

        behavior.finish(error_code=None)

        self.assertEqual(len(callback_count), 1, "Callback should only be called once")

    def test_finish_extracts_callback_atomically(self):
        """Phase 3: Verify finish() extracts callback atomically before stop()"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        callback = self.create_callback()

        behavior.start(callback=callback, parent=None)

        self.assertIsNotNone(behavior.callback)

        behavior.finish(error_code="TEST_ERROR")

        self.assertIsNone(behavior.callback)
        self.assertTrue(self.callback_called.is_set())
        self.assertEqual(self.callback_error_code, "TEST_ERROR")

    def test_finish_handles_callback_exceptions(self):
        """Phase 3: Verify finish() propagates exceptions from callback"""
        behavior = DummyBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        def bad_callback(error_code):
            raise ValueError("Callback error!")

        behavior.start(callback=bad_callback, parent=None)

        with self.assertRaises(ValueError):
            behavior.finish(error_code=None)

        self.assertEqual(behavior.state, BehaviorState.STOPPED)


if __name__ == "__main__":
    unittest.main()
