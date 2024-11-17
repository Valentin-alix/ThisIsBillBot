"""
Example demonstrating proper typing with get_sent_message and get_sent_messages.
This test shows how PyLance/Pylint can infer the correct message types.
"""

from D3Mapping.d3_mapping.resources.protos.game.chat_pb2 import (
    Channel,
    ChatChannelMessageRequest,
)

from src.core.behaviors.communication.chat_behavior import ChatBehavior
from tests.test_behaviors.behavior_test_base import BehaviorTestBase


class TestTypingExample(BehaviorTestBase):
    """Example showing proper typing inference."""

    def test_typing_with_get_sent_message(self):
        """Demonstrate that msg is properly typed as ChatChannelMessageRequest."""
        behavior = ChatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        self.start_behavior(behavior, content="Hello World!", channel=Channel.GLOBAL)
        assert self.wait_for_callback(timeout=1.0)

        # PyLance/Pylint infers msg as ChatChannelMessageRequest
        # So you get autocomplete and type checking for msg.content, msg.channel, etc.
        msg = self.get_sent_message(ChatChannelMessageRequest)

        # All these attributes are type-checked by PyLance
        assert msg.content == "Hello World!"
        assert msg.channel == Channel.GLOBAL
        # PyLance knows these exist and will show autocomplete

    def test_typing_with_get_sent_messages(self):
        """Demonstrate that messages list is properly typed."""
        behavior1 = ChatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )
        behavior2 = ChatBehavior(
            event_manager=self.event_manager,
            game_state=self.game_state,
            _logger=self.bot.logger,
        )

        self.start_behavior(behavior1, content="First message")
        assert self.wait_for_callback(timeout=1.0)

        self.clear_sent_messages()

        self.start_behavior(behavior2, content="Second message")
        assert self.wait_for_callback(timeout=1.0)

        # PyLance infers messages as list[ChatChannelMessageRequest]
        messages = self.get_sent_messages(ChatChannelMessageRequest)

        assert len(messages) == 1
        # PyLance knows messages[0] is ChatChannelMessageRequest
        assert messages[0].content == "Second message"

    def test_typing_with_index(self):
        """Demonstrate getting specific message by index."""
        for i in range(3):
            behavior = ChatBehavior(
                event_manager=self.event_manager,
                game_state=self.game_state,
                _logger=self.bot.logger,
            )
            self.start_behavior(behavior, content=f"Message {i}")
            assert self.wait_for_callback(timeout=1.0)

        # Get first message (index 0)
        first = self.get_sent_message(ChatChannelMessageRequest, index=0)
        assert first.content == "Message 0"

        # Get last message (index 2)
        last = self.get_sent_message(ChatChannelMessageRequest, index=2)
        assert last.content == "Message 2"
