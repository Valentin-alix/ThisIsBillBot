from D3Mapping.d3_mapping.resources.protos.game.chat_pb2 import (
    Channel,
    ChatChannelMessageRequest,
)
from src.core.behaviors.behavior import Behavior
from src.services.ai.human_solo_talk import HumanSoloTalk


class ChatBehavior(Behavior):
    """Behavior to send message in the chat, if you don't provide content then sentence will be generated from chatgpt"""

    def run(self, content: str | None = None, channel=Channel.GLOBAL) -> None:
        if content is None:
            content = HumanSoloTalk().get_solo_human_talk_in_general_msg(
                self.game_state.player.character_name
            )
        if content is None:
            self.logger.error("Did not get content from openapi ?!")
            return
        req = ChatChannelMessageRequest(content=content, channel=channel)
        self.event_manager.send(req)
        self.finish()
