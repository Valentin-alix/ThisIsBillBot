import unittest

from D3Mapping.d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUsedEvent,
    InteractiveUseErrorEvent,
    InteractiveUseRequest,
)
from src.core.behaviors.interactives.interactive_behavior import (
    InteractiveBehavior,
    InteractiveError,
)
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.engine.movements.map.map_data_adapter import DataMapProvider
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from tests.test_behaviors.behavior_test_base import BehaviorTestBase


class TestInteractiveBehavior(BehaviorTestBase):
    def setUp(self):
        super().setUp()
        data_map_provider = DataMapProvider(game_state=self.game_state)
        self.pathfinding = Pathfinding(
            data_map_provider=data_map_provider,
            game_state=self.game_state,
            logger=self.bot.logger,
        )
        self.map_move_behavior = MapMoveBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            path_finding=self.pathfinding,
        )
        self.behavior = InteractiveBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
            map_move_behavior=self.map_move_behavior,
            path_finding=self.pathfinding,
        )

    def test_use_interactive_without_movement(self):
        element_id = 123
        skill_instance_uid = 456

        # Start behavior without move_path (player at destination)
        self.start_behavior(
            self.behavior,
            move_path=None,
            element_id=element_id,
            skill_instance_uid=skill_instance_uid,
        )

        # Should send InteractiveUseRequest immediately
        self.assert_message_sent(InteractiveUseRequest, count=1)
        request = self.get_sent_message(InteractiveUseRequest)
        assert request.element_id == element_id
        assert request.skill_instance_uid == skill_instance_uid
        assert request.specific_instance_id == 0

        # Simulate server response
        response = InteractiveUsedEvent(element_id=element_id)
        self.inject_server_message(response)

        # Callback should be called
        assert self.wait_for_callback(timeout=1.0)
        self.assert_callback_success()

    def test_use_interactive_error(self):
        element_id = 123
        skill_instance_uid = 456

        self.start_behavior(
            self.behavior,
            move_path=None,
            element_id=element_id,
            skill_instance_uid=skill_instance_uid,
        )

        # Simulate error response
        self.inject_server_message(InteractiveUseErrorEvent())

        assert self.wait_for_callback(timeout=1.0)
        self.assert_callback_error(InteractiveError.USE_ERROR)

    def test_interactive_used_event_different_element(self):
        element_id = 123
        skill_instance_uid = 456

        self.start_behavior(
            self.behavior,
            move_path=None,
            element_id=element_id,
            skill_instance_uid=skill_instance_uid,
        )

        # Simulate response for different element
        self.inject_server_message(InteractiveUsedEvent(element_id=999))

        # Callback should NOT be called yet
        assert not self.callback_called.wait(timeout=0.1)

        # Now send correct element
        self.inject_server_message(InteractiveUsedEvent(element_id=element_id))

        assert self.wait_for_callback(timeout=1.0)
        self.assert_callback_success()

    def test_interactive_sends_correct_request(self):
        element_id = 789
        skill_instance_uid = 101112

        self.start_behavior(
            self.behavior,
            move_path=None,
            element_id=element_id,
            skill_instance_uid=skill_instance_uid,
        )

        # Verify request content
        self.assert_message_sent(InteractiveUseRequest, count=1)
        request = self.get_sent_message(InteractiveUseRequest)
        assert request.element_id == element_id
        assert request.skill_instance_uid == skill_instance_uid
        assert request.specific_instance_id == 0


if __name__ == "__main__":
    unittest.main()
