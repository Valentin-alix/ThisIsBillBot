from D3Mapping.d3_mapping.resources.protos.game.chat_pb2 import (
    Channel,
    ChatChannelMessageRequest,
)
from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.communication.chat_behavior import ChatBehavior
from tests.test_behaviors.behavior_test_base import BehaviorTestBase


class TestChatBehavior(BehaviorTestBase):
    """Test suite for ChatBehavior."""

    def test_send_custom_message(self):
        """Test sending a custom message to global chat."""
        behavior = ChatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        # Start behavior with custom content
        self.start_behavior(behavior, content="Hello World!", channel=Channel.GLOBAL)

        # Wait for callback
        assert self.wait_for_callback(timeout=1.0), "Behavior callback was not called"

        # Assert callback success
        self.assert_callback_success()

        # Assert message was sent
        self.assert_message_sent(ChatChannelMessageRequest, count=1)

        # Verify message content
        msg = self.get_sent_message(ChatChannelMessageRequest)
        assert msg.content == "Hello World!"
        assert msg.channel == Channel.GLOBAL

    def test_send_to_different_channel(self):
        """Test sending a message to a different channel."""
        behavior = ChatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        # Start behavior with team channel
        self.start_behavior(behavior, content="Team message", channel=Channel.TEAM)

        # Wait and verify
        assert self.wait_for_callback(timeout=1.0)
        self.assert_callback_success()

        # Verify channel
        msg = self.get_sent_message(ChatChannelMessageRequest)
        assert msg.channel == Channel.TEAM

    def test_behavior_stops_after_sending(self):
        """Test that behavior stops after sending message."""
        behavior = ChatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        self.start_behavior(behavior, content="Test")

        # Wait for callback
        assert self.wait_for_callback(timeout=1.0)

        # Behavior should be stopped
        assert not behavior.state == BehaviorState.RUNNING, (
            "Behavior should be stopped after finishing"
        )
