from DBDofusUnity.datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent

from src.core.engine.npcs.reply_selector import ByReplyId, ByText, resolve_reply_id

CONSULT_CHEST_REPLY_ID = 64361
OPEN_ACCOUNT_REPLY_ID = 64362


def _make_question(reply_ids: list[int]) -> NpcDialogQuestionEvent:
    msg = NpcDialogQuestionEvent(message_id=48366)
    for reply_id in reply_ids:
        msg.visible_replies.add().reply_id = reply_id
    return msg


def test_by_reply_id_returns_none_when_reply_is_not_offered() -> None:
    msg = _make_question([CONSULT_CHEST_REPLY_ID])

    assert resolve_reply_id(ByReplyId(reply_id=99999), msg) is None


def test_by_text_ignores_accents_and_case() -> None:
    msg = _make_question([OPEN_ACCOUNT_REPLY_ID])

    assert (
        resolve_reply_id(ByText(pattern=r"MODALITES D'OUVERTURE"), msg) == OPEN_ACCOUNT_REPLY_ID
    )
