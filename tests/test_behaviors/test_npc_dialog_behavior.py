from collections.abc import Callable

from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveEvent, DialogLeaveRequest
from datas.protos.non_obf.game.npc_pb2 import (
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
)
from dofus_unity_reader.game_constants.npc import NpcDialogInfo
from google.protobuf.message import Message

from src.core.behaviors.npcs.npc_dialog_behavior import NpcDialogBehavior
from src.core.engine.npcs.dialog_turn import DialogTurn
from src.core.engine.npcs.reply_selector import ByReplyId
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext

NPC_ID = 1440
SOUFFLER_REPLY_ID = 8996
LAST_SCREEN_MESSAGE_ID = 8901


def _make_behavior(game_state_ctx: GameStateContext, sent_messages: list[Message]) -> NpcDialogBehavior:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    event_manager.on_send_game_callback = sent_messages.append
    behavior = NpcDialogBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
    )

    def run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time
        func()

    behavior.run_timer = run_timer_inline
    return behavior


def _start(
    behavior: NpcDialogBehavior,
    turns: list[DialogTurn],
    finished: list[str | None] | None = None,
) -> None:
    behavior.game_state.entity.actor_by_id.clear()
    callback = None if finished is None else finished.append
    behavior.start(
        npc_dialog_info=NpcDialogInfo(npc_id=NPC_ID),
        turn_variants=[turns],
        callback=callback,
        parent=None,
    )


def _question(message_id: int, reply_ids: list[int]) -> NpcDialogQuestionEvent:
    msg = NpcDialogQuestionEvent(message_id=message_id)
    for reply_id in reply_ids:
        msg.visible_replies.add().reply_id = reply_id
    return msg


def test_a_question_without_reply_closes_the_dialog(game_state_ctx: GameStateContext) -> None:
    """Le PNJ a dit son dernier mot : sans DialogLeaveRequest le dialogue reste ouvert."""
    sent_messages: list[Message] = []
    behavior = _make_behavior(game_state_ctx, sent_messages)

    _start(behavior, [DialogTurn(reply=ByReplyId(reply_id=SOUFFLER_REPLY_ID))])
    behavior.event_manager.process_msg(_question(LAST_SCREEN_MESSAGE_ID, []))

    assert any(isinstance(message, DialogLeaveRequest) for message in sent_messages)


def test_the_behavior_finishes_when_the_server_closes_the_dialog(
    game_state_ctx: GameStateContext,
) -> None:
    sent_messages: list[Message] = []
    behavior = _make_behavior(game_state_ctx, sent_messages)
    finished: list[str | None] = []

    _start(behavior, [DialogTurn(reply=ByReplyId(reply_id=SOUFFLER_REPLY_ID))], finished)
    behavior.event_manager.process_msg(DialogLeaveEvent())

    assert finished == [None]


def test_a_declared_turn_is_answered(game_state_ctx: GameStateContext) -> None:
    sent_messages: list[Message] = []
    behavior = _make_behavior(game_state_ctx, sent_messages)

    _start(behavior, [DialogTurn(reply=ByReplyId(reply_id=SOUFFLER_REPLY_ID))])
    behavior.event_manager.process_msg(_question(8900, [SOUFFLER_REPLY_ID, 8997]))

    replies = [message for message in sent_messages if isinstance(message, NpcDialogReplyRequest)]
    assert [reply.reply_id for reply in replies] == [SOUFFLER_REPLY_ID]


def test_the_last_answer_no_longer_ends_the_behavior_on_its_own(
    game_state_ctx: GameStateContext,
) -> None:
    """Regression : finir des l'envoi laissait le dialogue ouvert et bloquait l'etape suivante."""
    sent_messages: list[Message] = []
    behavior = _make_behavior(game_state_ctx, sent_messages)
    finished: list[str | None] = []

    _start(behavior, [DialogTurn(reply=ByReplyId(reply_id=SOUFFLER_REPLY_ID))], finished)
    behavior.event_manager.process_msg(_question(8900, [SOUFFLER_REPLY_ID]))

    assert finished == []
