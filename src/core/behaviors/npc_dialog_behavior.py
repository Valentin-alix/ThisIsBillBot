from dataclasses import dataclass
from functools import partial

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveEvent
from d3_mapping.resources.protos.game.npc_pb2 import (
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
    NpcGenericActionRequest,
)

from src.core.behaviors.behavior import Behavior
from src.core.config.timings import BETWEEN_REPLY, ON_NEW_MAP_BEFORE_ACTION
from src.exceptions import UnexpectedStateException
from src.interfaces.models.npc_info import NpcInfo


@dataclass
class NpcDialogBehavior(Behavior):
    def run(self, npc_info: NpcInfo):
        self.event_manager.on(
            DialogLeaveEvent,
            callback=lambda _: self.finish(),
            once=True,
            originator=self,
        )
        self.run_timer(
            ON_NEW_MAP_BEFORE_ACTION,
            lambda: self.dialog_to_npc(
                npc_id=npc_info.npc_id,
                npc_action_id=npc_info.npc_action_id,
                npc_map_id=npc_info.npc_map_id,
                reply_ids=npc_info.reply_ids[::],
            ),
        )

    def dialog_to_npc(
        self,
        npc_id: int,
        npc_action_id,
        npc_map_id: int,
        reply_ids: list[int],
    ):
        self.event_manager.on(
            NpcDialogQuestionEvent,
            partial(self.on_npc_dialog_question_event, reply_ids=reply_ids),
            originator=self,
        )
        npc_request = NpcGenericActionRequest(
            npc_action_id=npc_action_id, npc_id=npc_id, npc_map_id=npc_map_id
        )
        self.event_manager.send(npc_request)

    def on_npc_dialog_question_event(
        self, msg: NpcDialogQuestionEvent, reply_ids: list[int]
    ):
        if not (len(reply_ids) > 0 and len(msg.visible_replies) > 0):
            raise UnexpectedStateException(
                f"NPC has {len(msg.visible_replies)} questions & not reply ids : {reply_ids}"
            )

        for reply in msg.visible_replies:
            if reply.reply_id not in reply_ids:
                continue
            reply_id = reply_ids.pop(reply_ids.index(reply.reply_id))
            npc_dialog_reply_request = NpcDialogReplyRequest(reply_id=reply_id)
            self.run_timer(
                BETWEEN_REPLY,
                lambda: self.event_manager.send(npc_dialog_reply_request),
            )
