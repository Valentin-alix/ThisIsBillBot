from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.dialog_pb2 import DialogLeaveEvent
from db_dofus_unity.protos.game.npc_pb2 import (
    NpcGenericActionRequest,
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
)
from src.common.logger import Logger
from src.consts import ON_NEW_MAP_BEFORE_ACTION, BASE_RANGE
from src.core.behaviors.behavior import Behavior


@dataclass
class NpcInfo:
    npc_action_id: int
    npc_id: int
    npc_map_id: int
    reply_ids: list[int]


@dataclass
class NpcDialogBehavior(Behavior):

    def run(self, npc_info: NpcInfo):
        self.dialog_to_npc(
            npc_id=npc_info.npc_id,
            npc_action_id=npc_info.npc_action_id,
            npc_map_id=npc_info.npc_map_id,
            reply_ids=npc_info.reply_ids,
        )

    def dialog_to_npc(
        self,
        npc_id: int,
        npc_action_id,
        npc_map_id: int,
        reply_ids: list[int],
    ):
        def _dialog_to_npc():
            self.event_manager.on(
                NpcDialogQuestionEvent,
                partial(self.on_npc_dialog_question_event, reply_ids=reply_ids),
                originator=self,
            )
            self.event_manager.on(
                DialogLeaveEvent,
                callback=lambda _: self.finish(),
                once=True,
                originator=self,
            )

            npc_request = NpcGenericActionRequest(
                npc_action_id=npc_action_id, npc_id=npc_id, npc_map_id=npc_map_id
            )
            self.event_manager.send(npc_request)

        self.run_timer(ON_NEW_MAP_BEFORE_ACTION, _dialog_to_npc)

    def on_npc_dialog_question_event(
        self, msg: NpcDialogQuestionEvent, reply_ids: list[int]
    ):
        if not len(reply_ids) > 0 and msg.visible_replies:
            return Logger().error(f"NPC has 0 questions & not reply ids ?")

        for reply in msg.visible_replies:
            if reply.reply_id not in reply_ids:
                continue
            reply_id = reply_ids.pop(reply_ids.index(reply.reply_id))
            npc_dialog_reply_request = NpcDialogReplyRequest(reply_id=reply_id)
            self.run_timer(
                BASE_RANGE,
                lambda: self.event_manager.send(npc_dialog_reply_request),
            )
