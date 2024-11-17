"""
Simplified tests for FightBehavior focusing on testable message handling.

These tests demonstrate:
1. Testing message-driven behavior lifecycle
2. Testing behavior completion conditions
3. Mocking complex dependencies to keep tests simple
"""

from unittest.mock import MagicMock

from D3Mapping.d3_mapping.resources.protos.game.fight_pb2 import (
    FightTurnStartPlayingEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.farms.fight.fight_movement_behavior import (
    FightMovementBehavior,
)
from src.core.behaviors.farms.fight.fight_preparation_behavior import (
    FightPreparationBehavior,
)
from src.core.behaviors.farms.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.farms.fight.fight_turn_behavior import FightTurnBehavior
from src.core.engine.fights.attack import Attacker
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.signals.shared_farm_signals import SharedSignals
from src.services.recorder import Recorder
from tests.test_behaviors.behavior_test_base import BehaviorTestBase


class TestFightBehaviorSimple(BehaviorTestBase):
    """Simplified test suite for FightBehavior focusing on message handling."""

    def setUp(self):
        super().setUp()

        # Mock all complex dependencies
        self.path_finding = MagicMock(spec=Pathfinding)
        self.fight_movement_behavior = MagicMock(spec=FightMovementBehavior)
        self.fight_spell_behavior = MagicMock(spec=FightSpellBehavior)
        self.attacker = MagicMock(spec=Attacker)
        self.fight_turn_behavior = MagicMock(spec=FightTurnBehavior)
        self.fight_preparation_behavior = MagicMock(spec=FightPreparationBehavior)
        self.recorder = Recorder()
        self.shared_signals = SharedSignals()

    def test_fight_behavior_registers_listeners_on_start(self):
        """Test that FightBehavior registers event listeners when started."""
        behavior = FightBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            path_finding=self.path_finding,
            fight_turn_behavior=self.fight_turn_behavior,
            fight_preparation_behavior=self.fight_preparation_behavior,
            recorder=self.recorder,
            shared_signals=self.shared_signals,
            login="TestBot",
        )

        # Check no listeners initially
        initial_map_listeners = len(
            self.event_manager.listeners_by_type_msg.get(
                MapComplementaryInformationEvent, []
            )
        )

        self.start_behavior(behavior)

        # Listeners should be registered
        final_map_listeners = len(
            self.event_manager.listeners_by_type_msg.get(
                MapComplementaryInformationEvent, []
            )
        )
        assert final_map_listeners > initial_map_listeners, (
            "FightBehavior should register listeners on start"
        )

    def test_fight_behavior_finishes_when_leaving_map(self):
        """Test that FightBehavior finishes when receiving MapComplementaryInformationEvent."""
        behavior = FightBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            path_finding=self.path_finding,
            fight_turn_behavior=self.fight_turn_behavior,
            fight_preparation_behavior=self.fight_preparation_behavior,
            recorder=self.recorder,
            shared_signals=self.shared_signals,
            login="TestBot",
        )

        self.start_behavior(behavior)

        # Behavior should be running
        assert behavior.state == BehaviorState.RUNNING, "Behavior should be running"
        assert not self.callback_called.is_set(), "Callback should not be called yet"

        # Simulate leaving fight (back to map)
        map_event = MapComplementaryInformationEvent()
        self.inject_server_message(map_event)

        # Behavior should finish
        assert self.wait_for_callback(timeout=1.0), (
            "Callback should be called when leaving fight"
        )
        self.assert_callback_success()
        assert not behavior.state == BehaviorState.RUNNING, "Behavior should be stopped"

    def test_fight_behavior_waits_for_fight_map_event(self):
        """Test that FightBehavior waits for FightMapInformationEvent."""
        behavior = FightBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            path_finding=self.path_finding,
            fight_turn_behavior=self.fight_turn_behavior,
            fight_preparation_behavior=self.fight_preparation_behavior,
            recorder=self.recorder,
            shared_signals=self.shared_signals,
            login="TestBot",
        )

        self.start_behavior(behavior)

        # Simulate fight map initialization
        fight_map_event = FightMapInformationEvent()
        self.inject_server_message(fight_map_event)

        # Behavior should still be running (waiting for fight to finish)
        assert behavior.state == BehaviorState.RUNNING, (
            "Behavior should still be running in fight"
        )
        assert not self.callback_called.is_set(), (
            "Behavior should not finish on fight start"
        )

    def test_fight_behavior_cleanup_removes_listeners(self):
        """Test that stopping FightBehavior cleans up event listeners."""
        behavior = FightBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            path_finding=self.path_finding,
            fight_turn_behavior=self.fight_turn_behavior,
            fight_preparation_behavior=self.fight_preparation_behavior,
            recorder=self.recorder,
            shared_signals=self.shared_signals,
            login="TestBot",
        )

        self.start_behavior(behavior)

        # Count listeners
        listeners_count = len(
            self.event_manager.listeners_by_type_msg.get(
                MapComplementaryInformationEvent, []
            )
        )
        assert listeners_count > 0, "Listeners should be registered"

        # Stop behavior
        behavior.stop()

        # Listeners should be cleaned up
        final_count = len(
            self.event_manager.listeners_by_type_msg.get(
                MapComplementaryInformationEvent, []
            )
        )
        assert final_count < listeners_count, "Listeners should be removed on cleanup"

    def test_fight_behavior_multiple_turn_events(self):
        """Test that FightBehavior can handle multiple turn events."""
        behavior = FightBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            path_finding=self.path_finding,
            fight_turn_behavior=self.fight_turn_behavior,
            fight_preparation_behavior=self.fight_preparation_behavior,
            recorder=self.recorder,
            shared_signals=self.shared_signals,
            login="TestBot",
        )

        # Initialize fight map first
        self.game_state.fight.is_map_fight_initialized = True

        self.start_behavior(behavior)

        # Send multiple turn events
        for i in range(3):
            turn_event = FightTurnStartPlayingEvent()
            self.inject_server_message(turn_event)

        # Behavior should still be running
        assert behavior.state == BehaviorState.RUNNING, (
            "Behavior should handle multiple turns"
        )

        # End fight
        map_event = MapComplementaryInformationEvent()
        self.inject_server_message(map_event)

        assert self.wait_for_callback(timeout=1.0)
        self.assert_callback_success()
