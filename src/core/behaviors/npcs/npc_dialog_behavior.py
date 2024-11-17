from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial
from typing import Callable

from D3Mapping.d3_mapping.resources.protos.game.npc_pb2 import (
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
    NpcGenericActionRequest,
)
from src.core.behaviors.behavior import Behavior
from src.core.config import BETWEEN_REPLY, ON_NEW_MAP_BEFORE_ACTION
from src.core.engine.npcs.npc_dialog_info import NpcDialogInfo, ReplyInfo


class NpcDialogErrorCode(StrEnum):
    FORBIDDEN_CONDITION = auto()
    UNEXPECTED_MESSAGE = auto()


@dataclass
class NpcDialogBehavior(Behavior):
    is_forbidden_msg_callback: Callable[[NpcDialogQuestionEvent], bool] | None = field(
        init=False, default=None
    )

    def run(
        self,
        npc_dialog_info: NpcDialogInfo,
        is_forbidden_msg_callback: Callable[[NpcDialogQuestionEvent], bool]
        | None = None,
    ):
        self.is_forbidden_msg_callback = is_forbidden_msg_callback
        self.run_timer(
            ON_NEW_MAP_BEFORE_ACTION,
            lambda: self.dialog_to_npc(npc_dialog_info=npc_dialog_info),
        )

    def dialog_to_npc(self, npc_dialog_info: NpcDialogInfo):
        self.event_manager.on(
            NpcDialogQuestionEvent,
            partial(
                self.on_npc_dialog_question_event,
                npc_dialog_info=npc_dialog_info,
            ),
            originator=self,
        )
        npc_request = NpcGenericActionRequest(
            npc_action_id=npc_dialog_info.npc_action_id,
            npc_id=npc_dialog_info.npc_id,
            npc_map_id=self.game_state.map.map_id,
        )
        self.event_manager.send(npc_request)

    def on_npc_dialog_question_event(
        self, msg: NpcDialogQuestionEvent, npc_dialog_info: NpcDialogInfo
    ):
        if self.is_forbidden_msg_callback and self.is_forbidden_msg_callback(msg):
            return self.finish(NpcDialogErrorCode.FORBIDDEN_CONDITION)

        if msg.message_id not in npc_dialog_info.reply_info_by_message_id:
            return self.finish(NpcDialogErrorCode.UNEXPECTED_MESSAGE)

        reply_info = npc_dialog_info.reply_info_by_message_id[msg.message_id]
        self.run_timer(BETWEEN_REPLY, lambda: self.send_npc_dialog_reply(reply_info))

    def send_npc_dialog_reply(self, reply_info: ReplyInfo):
        npc_dialog_reply_request = NpcDialogReplyRequest(reply_id=reply_info.reply_id)
        self.event_manager.send(npc_dialog_reply_request)
        if reply_info.do_finish_after:
            self.finish()
