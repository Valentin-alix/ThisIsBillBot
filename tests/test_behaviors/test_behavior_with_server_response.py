"""
Example test showing how to test a behavior that:
1. Sends a request to the server
2. Waits for a server response
3. Reacts to the response
"""

from D3Mapping.d3_mapping.resources.protos.game.chat_pb2 import (
    Channel,
    ChatChannelMessageEvent,
    ChatChannelMessageRequest,
)
from src.core.behaviors.behavior import Behavior, BehaviorState
from tests.test_behaviors.behavior_test_base import BehaviorTestBase


class WaitForChatResponseBehavior(Behavior):
    """Example behavior that waits for a chat response from server."""

    def run(self, message: str) -> None:
        # Send chat message
        req = ChatChannelMessageRequest(content=message, channel=Channel.GLOBAL)
        self.event_manager.send(req)

        # Listen for server response
        self.event_manager.on(ChatChannelMessageEvent, self._on_chat_response, self)

    def _on_chat_response(self, msg: ChatChannelMessageEvent):
        # When we receive a chat message, finish successfully
        self.finish()


class TestBehaviorWithServerResponse(BehaviorTestBase):
    """Test behaviors that wait for server responses."""

    def test_behavior_waits_for_server_response(self):
        """Test that behavior waits for and reacts to server messages."""
        behavior = WaitForChatResponseBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        # Start behavior
        self.start_behavior(behavior, message="Hello")

        # Verify request was sent
        self.assert_message_sent(ChatChannelMessageRequest, count=1)

        # Behavior should still be running, waiting for response
        assert behavior.state == BehaviorState.RUNNING, (
            "Behavior should be waiting for response"
        )

        # Callback should not be called yet
        assert not self.callback_called.is_set(), "Callback should not be called yet"

        # Simulate server response
        server_response = ChatChannelMessageEvent(
            content="Hello back!",
            sender_name="Server",
            channel=Channel.GLOBAL,
        )
        self.inject_server_message(server_response)

        # Now callback should be called
        assert self.wait_for_callback(timeout=1.0), (
            "Callback should be called after server response"
        )
        self.assert_callback_success()

        # Behavior should be stopped
        assert not behavior.state == BehaviorState.RUNNING, "Behavior should be stopped"

    def test_behavior_cleanup_on_stop(self):
        """Test that behavior properly cleans up listeners when stopped."""
        behavior = WaitForChatResponseBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        # Start behavior
        self.start_behavior(behavior, message="Test")

        # Get initial listener count
        initial_listeners = len(
            self.event_manager.listeners_by_type_msg.get(ChatChannelMessageEvent, [])
        )
        assert initial_listeners > 0, "Behavior should have registered listeners"

        # Stop behavior
        behavior.stop()

        # Listeners should be cleared
        remaining_listeners = len(
            self.event_manager.listeners_by_type_msg.get(ChatChannelMessageEvent, [])
        )
        assert remaining_listeners < initial_listeners, "Listeners should be cleaned up"
