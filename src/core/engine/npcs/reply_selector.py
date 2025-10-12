from typing import Annotated, Literal

from DBDofusUnity.datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent
from pydantic import BaseModel, Field

from src.core.engine.npcs.dialog_texts import get_reply_text, matches


class ByText(BaseModel):
    kind: Literal["text"] = "text"
    pattern: str


class ByReplyId(BaseModel):
    kind: Literal["reply_id"] = "reply_id"
    reply_id: int


type ReplySelector = Annotated[ByText | ByReplyId, Field(discriminator="kind")]


def resolve_reply_id(selector: ReplySelector, msg: NpcDialogQuestionEvent) -> int | None:
    match selector:
        case ByText():
            return _resolve_by_text(selector, msg)
        case ByReplyId():
            return _resolve_by_reply_id(selector, msg)


def _resolve_by_text(selector: ByText, msg: NpcDialogQuestionEvent) -> int | None:
    for visible_reply in msg.visible_replies:
        if matches(selector.pattern, get_reply_text(visible_reply.reply_id)):
            return visible_reply.reply_id
    return None


def _resolve_by_reply_id(selector: ByReplyId, msg: NpcDialogQuestionEvent) -> int | None:
    for visible_reply in msg.visible_replies:
        if visible_reply.reply_id == selector.reply_id:
            return selector.reply_id
    return None
