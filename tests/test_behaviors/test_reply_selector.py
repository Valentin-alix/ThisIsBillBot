from datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent

from src.core.engine.quests.reply_selector import (
    ByIndex,
    ByQuestAction,
    ByReplyId,
    resolve_reply_id,
)


def _make_question(reply_ids: list[int]) -> NpcDialogQuestionEvent:
    msg = NpcDialogQuestionEvent(message_id=48366)
    for reply_id in reply_ids:
        msg.visible_replies.add().reply_id = reply_id
    return msg


def test_by_reply_id_returns_the_reply_when_visible() -> None:
    msg = _make_question([64361, 64362])

    assert resolve_reply_id(ByReplyId(reply_id=64362), msg) == 64362


def test_by_reply_id_returns_none_when_reply_is_not_offered() -> None:
    msg = _make_question([64361])

    assert resolve_reply_id(ByReplyId(reply_id=99999), msg) is None


def test_by_index_returns_the_nth_visible_reply() -> None:
    msg = _make_question([64361, 64362, 64363])

    assert resolve_reply_id(ByIndex(index=0), msg) == 64361
    assert resolve_reply_id(ByIndex(index=2), msg) == 64363


def test_by_index_returns_none_when_out_of_range() -> None:
    msg = _make_question([64361])

    assert resolve_reply_id(ByIndex(index=1), msg) is None
    assert resolve_reply_id(ByIndex(index=-1), msg) is None


def test_by_quest_action_matches_the_reply_carrying_the_action() -> None:
    msg = _make_question([64361, 64362])
    msg.visible_replies[1].actions.add().id = 4242

    assert resolve_reply_id(ByQuestAction(action_id=4242), msg) == 64362


def test_by_quest_action_returns_none_without_mapped_actions() -> None:
    """`VisibleReply.actions` is absent from game_mappings.json, so it decodes empty."""
    msg = _make_question([64361, 64362])

    assert resolve_reply_id(ByQuestAction(action_id=4242), msg) is None
