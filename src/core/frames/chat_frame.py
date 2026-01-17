from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.chat_pb2 import (
    Channel,
    ChatChannelMessageEvent,
    ChatPrivateMessageRequest,
)

from src.core.frames.frame import Frame
from src.services.ai.human_response import get_private_message_response


@dataclass
class ChatFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(
            ChatChannelMessageEvent,
            self.on_chat_channel_message_event,
            originator=self,
            priority=self.priority,
        )

    def on_chat_channel_message_event(self, msg: ChatChannelMessageEvent):
        if self.is_playing_event.is_set() and msg.channel == Channel.PRIVATE:
            self.logger.info("Message in private received")
            response_content = get_private_message_response(msg.content)
            if response_content is None:
                return
            self.run_timer(
                (3, 6),
                lambda: self.event_manager.send(
                    ChatPrivateMessageRequest(content=response_content, name=msg.sender_name)
                ),
            )
