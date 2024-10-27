from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial
from typing import Callable, Iterable

from d3_mapping.resources.protos.game.dialog_pb2 import (
    DialogLeaveEvent,
    DialogLeaveRequest,
)
from d3_mapping.resources.protos.game.npc_pb2 import (
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
    NpcGenericActionRequest,
)

from src.core.behaviors.behavior import Behavior
from src.core.config.timings import BETWEEN_REPLY, ON_NEW_MAP_BEFORE_ACTION
from src.interfaces.models.npc_info import NpcDialogInfo


class NpcDialogErrorCode(StrEnum):
    FORBIDDEN_CONDITION = auto()
    NO_EXPECTED_REPLY = auto()


@dataclass
class NpcDialogBehavior(Behavior):
    _forbidden_condition_dialog_param: Callable[[Iterable[str]], bool] | None = field(
        init=False, default=None
    )

    def run(
        self,
        npc_dialog_info: NpcDialogInfo,
        forbidden_condition_dialog_param: Callable[[Iterable[str]], bool] | None = None,
    ):
        self._forbidden_condition_dialog_param = forbidden_condition_dialog_param
        self.event_manager.on(
            DialogLeaveEvent,
            callback=lambda _: self.finish(),
            once=True,
            originator=self,
        )
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
        if (
            self._forbidden_condition_dialog_param
            and self._forbidden_condition_dialog_param(msg.dialog_params)
        ):
            return self.leave_dialogs(NpcDialogErrorCode.FORBIDDEN_CONDITION)

        for reply in msg.visible_replies:
            if (
                (
                    npc_dialog_info.include_reply_ids is not None
                    and reply.reply_id not in npc_dialog_info.include_reply_ids
                )
                or (reply.reply_id in npc_dialog_info.exclude_reply_ids)
                or any(
                    action.id in npc_dialog_info.exclude_action_ids
                    for action in reply.actions
                )
            ):
                continue
            reply_id = reply.reply_id
            npc_dialog_reply_request = NpcDialogReplyRequest(reply_id=reply_id)
            return self.run_timer(
                BETWEEN_REPLY,
                lambda: self.event_manager.send(npc_dialog_reply_request),
            )

    def leave_dialogs(self, error_code: str | None):
        self.event_manager.on(
            DialogLeaveEvent,
            callback=lambda _: self.finish(error_code=error_code),
            originator=self,
        )
        req = DialogLeaveRequest()
        self.event_manager.send(req)
        self.event_manager.send(req)
