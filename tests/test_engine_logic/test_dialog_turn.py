from datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent

from src.core.engine.npcs.dialog_turn import DialogTurn, DialogTurns, DialogVariants
from src.core.engine.npcs.reply_selector import ByReplyId, ByText

KERUBIM_SHOP_CLOSED_MESSAGE_ID = 12877
KERUBIM_LISTEN_MESSAGE_ID = 13470
KERUBIM_HELP_REPLY_ID = 15482
KERUBIM_LISTEN_REPLY_ID = 15483


def _make_question(message_id: int, reply_ids: list[int]) -> NpcDialogQuestionEvent:
    msg = NpcDialogQuestionEvent(message_id=message_id)
    for reply_id in reply_ids:
        msg.visible_replies.add().reply_id = reply_id
    return msg


def test_each_question_gets_its_declared_turn() -> None:
    turns = DialogTurns(
        turns=[
            DialogTurn(message_id=1, reply=ByReplyId(reply_id=10)),
            DialogTurn(message_id=2, reply=ByReplyId(reply_id=20), finish_after=True),
        ]
    )

    first = turns.take_reply_for(_make_question(1, [10, 11]))
    second = turns.take_reply_for(_make_question(2, [20, 21]))

    assert first is not None
    assert first.reply_id == 10
    assert first.do_finish_after is False
    assert second is not None
    assert second.reply_id == 20
    assert second.do_finish_after is True


def test_questions_asked_out_of_order_still_resolve() -> None:
    """A walkthrough gives an unreliable question order, so turns are not consumed in order."""
    turns = DialogTurns(
        turns=[
            DialogTurn(message_id=1, reply=ByReplyId(reply_id=10)),
            DialogTurn(message_id=2, reply=ByReplyId(reply_id=20)),
        ]
    )

    second = turns.take_reply_for(_make_question(2, [20]))
    first = turns.take_reply_for(_make_question(1, [10]))

    assert second is not None
    assert second.reply_id == 20
    assert first is not None
    assert first.reply_id == 10


def test_a_turn_answers_only_once() -> None:
    """Two identical questions need two declared turns, otherwise the dialog would loop."""
    turns = DialogTurns(turns=[DialogTurn(message_id=1, reply=ByReplyId(reply_id=10))])

    assert turns.take_reply_for(_make_question(1, [10])) is not None
    assert turns.take_reply_for(_make_question(1, [10])) is None


def test_a_turn_without_message_id_matches_any_question() -> None:
    turns = DialogTurns(turns=[DialogTurn(reply=ByReplyId(reply_id=11), finish_after=True)])

    reply_info = turns.take_reply_for(_make_question(48366, [10, 11]))

    assert reply_info is not None
    assert reply_info.reply_id == 11


def test_an_unexpected_question_resolves_to_no_reply() -> None:
    turns = DialogTurns(turns=[DialogTurn(message_id=1, reply=ByReplyId(reply_id=10))])

    assert turns.take_reply_for(_make_question(999, [10])) is None


def test_message_pattern_restricts_a_turn_to_one_question() -> None:
    turns = DialogTurns(
        turns=[DialogTurn(message_pattern=r"boutique est fermee", reply=ByReplyId(reply_id=10))]
    )

    assert turns.take_reply_for(_make_question(KERUBIM_SHOP_CLOSED_MESSAGE_ID, [10])) is not None


def test_message_pattern_ignores_a_question_it_does_not_describe() -> None:
    turns = DialogTurns(
        turns=[DialogTurn(message_pattern=r"boutique est fermee", reply=ByReplyId(reply_id=10))]
    )

    assert turns.take_reply_for(_make_question(KERUBIM_LISTEN_MESSAGE_ID, [10])) is None


def test_by_text_picks_the_reply_from_its_wording() -> None:
    turns = DialogTurns(turns=[DialogTurn(reply=ByText(pattern=r"accepter de l'aider"))])

    reply_info = turns.take_reply_for(
        _make_question(KERUBIM_LISTEN_MESSAGE_ID, [KERUBIM_LISTEN_REPLY_ID, KERUBIM_HELP_REPLY_ID])
    )

    assert reply_info is not None
    assert reply_info.reply_id == KERUBIM_HELP_REPLY_ID


def test_by_text_matching_no_offered_reply_resolves_to_nothing() -> None:
    turns = DialogTurns(turns=[DialogTurn(reply=ByText(pattern=r"accepter de l'aider"))])

    assert (
        turns.take_reply_for(_make_question(KERUBIM_LISTEN_MESSAGE_ID, [KERUBIM_LISTEN_REPLY_ID]))
        is None
    )


def test_a_single_variant_behaves_like_a_plain_turn_list() -> None:
    variants = DialogVariants.from_turn_variants([[DialogTurn(message_id=1, reply=ByReplyId(reply_id=10))]])

    reply_info = variants.take_reply_for(_make_question(1, [10]))

    assert reply_info is not None
    assert reply_info.reply_id == 10
    assert variants.active_index == 0


def test_the_variant_answering_the_first_question_becomes_the_active_one() -> None:
    """A quest already done offers another dialog path, recognizable from its first reply."""
    variants = DialogVariants.from_turn_variants(
        [
            [
                DialogTurn(reply=ByReplyId(reply_id=10)),
                DialogTurn(reply=ByReplyId(reply_id=11), finish_after=True),
            ],
            [
                DialogTurn(reply=ByReplyId(reply_id=20)),
                DialogTurn(reply=ByReplyId(reply_id=21), finish_after=True),
            ],
        ]
    )

    first = variants.take_reply_for(_make_question(1, [20, 99]))
    second = variants.take_reply_for(_make_question(2, [21, 99]))

    assert first is not None
    assert first.reply_id == 20
    assert variants.active_index == 1
    assert second is not None
    assert second.reply_id == 21
    assert second.do_finish_after is True


def test_a_variant_that_stops_answering_falls_back_to_another_one() -> None:
    variants = DialogVariants.from_turn_variants(
        [
            [DialogTurn(reply=ByReplyId(reply_id=10))],
            [DialogTurn(reply=ByReplyId(reply_id=20))],
        ]
    )

    first = variants.take_reply_for(_make_question(1, [10]))
    second = variants.take_reply_for(_make_question(2, [20]))

    assert first is not None
    assert first.reply_id == 10
    assert second is not None
    assert second.reply_id == 20
    assert variants.active_index == 1


def test_a_question_no_variant_answers_resolves_to_no_reply() -> None:
    variants = DialogVariants.from_turn_variants(
        [
            [DialogTurn(reply=ByReplyId(reply_id=10))],
            [DialogTurn(reply=ByReplyId(reply_id=20))],
        ]
    )

    assert variants.take_reply_for(_make_question(1, [99])) is None
    assert variants.active_index is None
