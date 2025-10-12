from dataclasses import dataclass, field

from DBDofusUnity.datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent
from DBDofusUnity.dofus_unity_reader.game_constants.npc import ReplyInfo
from pydantic import BaseModel

from src.core.engine.npcs.dialog_texts import get_question_text, matches
from src.core.engine.npcs.reply_selector import ReplySelector, resolve_reply_id


class DialogTurn(BaseModel):
    message_id: int | None = None
    message_pattern: str | None = None
    reply: ReplySelector
    finish_after: bool = False

    def fits(self, msg: NpcDialogQuestionEvent) -> bool:
        if self.message_id is not None and self.message_id != msg.message_id:
            return False
        if self.message_pattern is not None and not matches(
            self.message_pattern, get_question_text(msg.message_id)
        ):
            return False
        return True


@dataclass
class DialogTurns:
    turns: list[DialogTurn]
    _remaining_indexes: list[int] = field(init=False, default_factory=list[int])

    def __post_init__(self) -> None:
        self._remaining_indexes = list(range(len(self.turns)))

    def take_reply_for(self, msg: NpcDialogQuestionEvent) -> ReplyInfo | None:
        for position, turn_index in enumerate(self._remaining_indexes):
            turn = self.turns[turn_index]
            if not turn.fits(msg):
                continue
            reply_id = resolve_reply_id(turn.reply, msg)
            if reply_id is None:
                continue
            del self._remaining_indexes[position]
            return ReplyInfo(reply_id=reply_id, do_finish_after=turn.finish_after)
        return None


@dataclass
class DialogVariants:
    """Alternative dialog paths for the same step, e.g. a quest already done offers a shorter path."""

    variants: list[DialogTurns]
    _active_index: int | None = field(init=False, default=None)

    @classmethod
    def from_turn_variants(cls, turn_variants: list[list[DialogTurn]]) -> "DialogVariants":
        return cls(variants=[DialogTurns(turns=turns) for turns in turn_variants])

    @property
    def active_index(self) -> int | None:
        return self._active_index

    def take_reply_for(self, msg: NpcDialogQuestionEvent) -> ReplyInfo | None:
        for variant_index in self._search_order():
            reply_info = self.variants[variant_index].take_reply_for(msg)
            if reply_info is None:
                continue
            self._active_index = variant_index
            return reply_info
        return None

    def _search_order(self) -> list[int]:
        indexes = list(range(len(self.variants)))
        if self._active_index is None:
            return indexes
        return [self._active_index, *(index for index in indexes if index != self._active_index)]
