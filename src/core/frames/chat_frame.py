from dataclasses import dataclass

from d3_mapping.resources.protos.game.chat_pb2 import (
    Channel,
    ChatChannelMessageEvent,
    ChatPrivateMessageRequest,
)

from src.core.frames.frame import Frame
from src.core.logic.chat.human_response import get_human_response_to_private_msg


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
            response_content = get_human_response_to_private_msg(
                msg.content, self.game_state.player.character_name, msg.sender_name
            )
            if response_content is None:
                return
            self.run_timer(
                (3, 6),
                lambda: self.event_manager.send(
                    ChatPrivateMessageRequest(
                        content=response_content, name=msg.sender_name
                    )
                ),
            )
