from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.dialog_pb2 import DialogLeaveEvent
from db_dofus_unity.protos.game.npc_pb2 import (
    NpcGenericActionRequest,
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
)
from src.core.behaviors.behavior import Behavior, EndCode
from src.core.behaviors.movements.auto_trip_behavior import AutoTripBehavior


@dataclass
class NpcDialogBehavior(Behavior):
    auto_trip_behavior: AutoTripBehavior

    def run(self, npc_id: int, npc_action_id, npc_map_id: int, reply_ids: list[int]):
        self.auto_trip_behavior.start(
            parent=self,
            callback=partial(
                self.on_arrived_to_npc_map,
                npc_id=npc_id,
                npc_action_id=npc_action_id,
                npc_map_id=npc_map_id,
                reply_ids=reply_ids,
            ),
            map_id=npc_map_id,
        )

    def on_arrived_to_npc_map(
        self,
        code: EndCode,
        npc_id: int,
        npc_action_id,
        npc_map_id: int,
        reply_ids: list[int],
    ):
        if code is not EndCode.SUCCESS:
            return
        self.event_manager.on(
            NpcDialogQuestionEvent,
            partial(self.on_npc_dialog_question_event, reply_ids=reply_ids),
            originator=self,
        )
        self.event_manager.on(
            DialogLeaveEvent, callback=self.finish, once=True, originator=self
        )

        npc_request = NpcGenericActionRequest(
            npc_action_id=npc_action_id, npc_id=npc_id, npc_map_id=npc_map_id
        )
        self.event_manager.send(npc_request)

    def on_npc_dialog_question_event(
        self, msg: NpcDialogQuestionEvent, reply_ids: list[int]
    ):
        if len(reply_ids) > 0 and msg.visible_replies:
            for reply in msg.visible_replies:
                if reply.reply_id not in reply_ids:
                    continue
                reply_id = reply_ids.pop(reply_ids.index(reply.reply_id))
                npc_dialog_reply_request = NpcDialogReplyRequest(reply_id=reply_id)
                self.event_manager.send(npc_dialog_reply_request)
