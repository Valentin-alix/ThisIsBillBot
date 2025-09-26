from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto

from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveEvent, DialogLeaveRequest
from datas.protos.non_obf.game.npc_pb2 import (
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
    NpcGenericActionRequest,
)
from dofus_unity_reader.game_constants.npc import NpcDialogInfo, ReplyInfo

from src.core.behaviors.behavior import Behavior
from src.core.engine.npcs.dialog_texts import get_question_text
from src.core.engine.npcs.dialog_turn import DialogTurn, DialogVariants
from src.services.human_timings import HumanTimingsService


class NpcDialogErrorCode(StrEnum):
    FORBIDDEN_CONDITION = auto()
    UNEXPECTED_MESSAGE = auto()


@dataclass
class NpcDialogBehavior(Behavior):
    is_forbidden_msg_callback: Callable[[NpcDialogQuestionEvent], bool] | None = field(
        init=False, default=None
    )
    _variants: DialogVariants = field(
        init=False, default_factory=lambda: DialogVariants.from_turn_variants([[]])
    )

    def run(
        self,
        npc_dialog_info: NpcDialogInfo,
        turn_variants: list[list[DialogTurn]] | None = None,
        is_forbidden_msg_callback: Callable[[NpcDialogQuestionEvent], bool] | None = None,
    ):
        self.is_forbidden_msg_callback = is_forbidden_msg_callback
        self._variants = DialogVariants.from_turn_variants(turn_variants or [[]])
        self.run_timer(
            HumanTimingsService().get_timing_after_map_arrival(),
            lambda: self.dialog_to_npc(npc_dialog_info=npc_dialog_info),
        )

    def dialog_to_npc(self, npc_dialog_info: NpcDialogInfo) -> None:
        self.ensure_dialog_closed(lambda: self.talk_to_npc(npc_dialog_info))

    def talk_to_npc(self, npc_dialog_info: NpcDialogInfo) -> None:
        self.event_manager.on(
            NpcDialogQuestionEvent,
            self.on_npc_dialog_question_event,
            originator=self,
        )
        self.event_manager.on(
            DialogLeaveEvent,
            self.on_dialog_leave_event,
            originator=self,
        )
        npc_id = self.game_state.entity.resolve_npc_id(npc_dialog_info)
        npc_request = NpcGenericActionRequest(
            npc_action_id=npc_dialog_info.npc_action_id, npc_id=npc_id, npc_map_id=self.game_state.map.map_id
        )
        self.event_manager.send(npc_request)

    def on_dialog_leave_event(self, msg: DialogLeaveEvent) -> None:
        del msg
        self.finish()

    def on_npc_dialog_question_event(self, msg: NpcDialogQuestionEvent):
        if self.is_forbidden_msg_callback and self.is_forbidden_msg_callback(msg):
            return self.finish(NpcDialogErrorCode.FORBIDDEN_CONDITION)

        if not msg.visible_replies:
            self.logger.info("NPC said its last word, leaving the dialog")
            return self.event_manager.send(DialogLeaveRequest())

        previous_variant_index = self._variants.active_index
        reply_info = self._variants.take_reply_for(msg)
        if reply_info is None:
            self.logger.warning(
                f"No declared turn answers question {msg.message_id} ({get_question_text(msg.message_id)!r})"
            )
            return self.finish(NpcDialogErrorCode.UNEXPECTED_MESSAGE)

        if previous_variant_index is not None and previous_variant_index != self._variants.active_index:
            self.logger.info(
                f"Dialog variant {previous_variant_index} exhausted, "
                f"switching to variant {self._variants.active_index}"
            )

        timing = HumanTimingsService().get_timing_npc_dialog_reply()
        self.run_timer(timing, lambda: self.send_npc_dialog_reply(reply_info))

    def send_npc_dialog_reply(self, reply_info: ReplyInfo):
        npc_dialog_reply_request = NpcDialogReplyRequest(reply_id=reply_info.reply_id)
        self.event_manager.send(npc_dialog_reply_request)
        if reply_info.do_finish_after:
            self.finish()
