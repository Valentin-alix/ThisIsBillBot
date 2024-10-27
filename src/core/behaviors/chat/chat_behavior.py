from wonderwords import RandomSentence
from d3_mapping.resources.protos.game.chat_pb2 import (
    Channel,
    ChatChannelMessageEvent,
    ChatChannelMessageRequest,
)

from src.core.behaviors.behavior import Behavior


class ChatBehavior(Behavior):
    """Behavior to send message in the chat, if you don't provide content then random words will be generated"""

    def run(self, content: str | None = None, channel=Channel.GLOBAL) -> None:
        self.event_manager.on(
            ChatChannelMessageEvent, lambda _: self.finish(), originator=self
        )
        if content is None:
            content = self.get_random_sentence()
        req = ChatChannelMessageRequest(content=content, channel=channel)
        self.event_manager.send(req)

    def get_random_sentence(self) -> str:
        random_sentence = RandomSentence()
        return (
            random_sentence.simple_sentence().lower().replace(",", "").replace(".", "")
        )
