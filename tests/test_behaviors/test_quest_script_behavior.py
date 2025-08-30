from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

from datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent
from datas.protos.non_obf.game.quest_pb2 import QuestValidatedEvent
from dofus_unity_reader.game_constants.npc import ReplyInfo

from src.core.behaviors.quests.quest_script_behavior import (
    QuestScriptBehavior,
    QuestScriptError,
)
from src.core.engine.quests.quest_script import (
    DialogTurn,
    EnsureItemStep,
    FightStep,
    GoToStep,
    QuestScript,
    QuestStep,
    TalkToNpcStep,
)
from src.core.engine.quests.reply_selector import ByIndex, ByReplyId
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext

QUEST_ID = 2510
NPC_ID = 1901
START_MAP_ID = 100
DESTINATION_MAP_ID = 200
DESTINATION_MAP_IDS = {DESTINATION_MAP_ID}
OTHER_MAP_IDS = {300}


def _make_behavior(game_state_ctx: GameStateContext) -> QuestScriptBehavior:
    game_state_ctx.game_state.map.map_id = START_MAP_ID
    game_state_ctx.game_state.player.level = 200
    behavior = QuestScriptBehavior(
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        auto_trip_smart_behavior=MagicMock(),
        npc_dialog_behavior=MagicMock(),
        attacker_behavior=MagicMock(),
        interactive_behavior=MagicMock(),
        sale_hotel_buy_behavior=MagicMock(),
    )

    def run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time
        func()

    # Run timers inline so the step loop is deterministic.
    behavior.run_timer = run_timer_inline
    return behavior


def _mock_of(child_behavior: object) -> MagicMock:
    return cast(MagicMock, child_behavior)


def _callback_recording_into(finished: list[str | None]) -> Callable[..., None]:
    def callback(error_code: str | None, *_args: object, **_kwargs: object) -> None:
        finished.append(error_code)

    return callback


def _child_callback(child_behavior: object) -> Callable[..., None]:
    return cast(Callable[..., None], _mock_of(child_behavior).start.call_args.kwargs["callback"])


def _child_kwarg(child_behavior: object, name: str) -> object:
    return _mock_of(child_behavior).start.call_args.kwargs[name]


def _arrive(behavior: QuestScriptBehavior, map_id: int) -> None:
    """Simulate the travel behavior reaching `map_id` and reporting success."""
    behavior.game_state.map.map_id = map_id
    _child_callback(behavior.auto_trip_smart_behavior)(None)


def _start(
    behavior: QuestScriptBehavior,
    script: QuestScript,
    finished: list[str | None] | None = None,
) -> None:
    callback = _callback_recording_into(finished) if finished is not None else None
    behavior.start(script=script, callback=callback, parent=None)


def test_script_runs_its_steps_in_order(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [
        GoToStep(map_ids=DESTINATION_MAP_IDS),
        FightStep(count=2, map_ids=DESTINATION_MAP_IDS),
    ]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)
    # Step 0 travels; on arrival step 1 is already on the destination and attacks straight away.
    _arrive(behavior, DESTINATION_MAP_ID)

    _mock_of(behavior.attacker_behavior).start.assert_called_once()
    assert _child_kwarg(behavior.attacker_behavior, "count_fight_limit") == 2
    assert finished == []

    _child_callback(behavior.attacker_behavior)(None, 2)

    assert finished == [None]


def test_travel_is_skipped_when_already_on_destination(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.map.map_id = DESTINATION_MAP_ID
    steps: list[QuestStep] = [FightStep(map_ids=DESTINATION_MAP_IDS)]

    _start(behavior, QuestScript(name="demo", steps=steps))

    _mock_of(behavior.auto_trip_smart_behavior).start.assert_not_called()
    _mock_of(behavior.attacker_behavior).start.assert_called_once()


def test_script_resumes_at_the_server_step(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.quest.set_current_step_id(QUEST_ID, 56)
    steps: list[QuestStep] = [
        GoToStep(map_ids=OTHER_MAP_IDS),
        GoToStep(map_ids=OTHER_MAP_IDS),
        FightStep(map_ids=DESTINATION_MAP_IDS),
    ]

    _start(
        behavior,
        QuestScript(
            name="demo",
            quest_id=QUEST_ID,
            steps=steps,
            server_step_id_by_index={0: 55, 2: 56},
        ),
    )

    # It jumped straight to step 2, so it travels to the fight destination.
    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == DESTINATION_MAP_IDS


def test_script_starts_at_zero_when_server_step_is_unmapped(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.quest.set_current_step_id(QUEST_ID, 999)
    steps: list[QuestStep] = [GoToStep(map_ids=OTHER_MAP_IDS), FightStep()]

    _start(
        behavior,
        QuestScript(
            name="demo", quest_id=QUEST_ID, steps=steps, server_step_id_by_index={0: 55}
        ),
    )

    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == OTHER_MAP_IDS


def test_quest_validated_event_finishes_early(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.map.map_id = DESTINATION_MAP_ID
    steps: list[QuestStep] = [
        FightStep(map_ids=DESTINATION_MAP_IDS),
        FightStep(map_ids=DESTINATION_MAP_IDS),
    ]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", quest_id=QUEST_ID, steps=steps), finished)
    behavior.event_manager.process_msg(QuestValidatedEvent(quest_id=QUEST_ID))

    assert finished == [None]
    # The second fight never started.
    assert _mock_of(behavior.attacker_behavior).start.call_count == 1


def test_level_too_low_aborts_before_any_step(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.player.level = 10
    steps: list[QuestStep] = [FightStep()]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", level_min=50, steps=steps), finished)

    assert finished == [QuestScriptError.LEVEL_TOO_LOW]
    _mock_of(behavior.auto_trip_smart_behavior).start.assert_not_called()


def test_missing_item_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [EnsureItemStep(item_gid=311, quantity=1)]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.ITEM_MISSING]


def test_child_error_propagates_to_the_callback(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [FightStep(map_ids=DESTINATION_MAP_IDS)]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)
    _child_callback(behavior.auto_trip_smart_behavior)("path_not_found")

    assert finished == ["path_not_found"]


def test_unknown_coord_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [GoToStep(coord=(9999, 9999))]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.UNKNOWN_DESTINATION]


# --- dialog turns ----------------------------------------------------------


def _make_question(message_id: int, reply_ids: list[int]) -> NpcDialogQuestionEvent:
    msg = NpcDialogQuestionEvent(message_id=message_id)
    for reply_id in reply_ids:
        msg.visible_replies.add().reply_id = reply_id
    return msg


def _resolve_reply_of(behavior: QuestScriptBehavior) -> Callable[[NpcDialogQuestionEvent], ReplyInfo | None]:
    return cast(
        Callable[[NpcDialogQuestionEvent], ReplyInfo | None],
        _child_kwarg(behavior.npc_dialog_behavior, "resolve_reply"),
    )


def _start_dialog_script(
    game_state_ctx: GameStateContext, turns: list[DialogTurn]
) -> QuestScriptBehavior:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [TalkToNpcStep(npc_id=NPC_ID, turns=turns)]
    _start(behavior, QuestScript(name="demo", steps=steps))
    return behavior


def test_dialog_turns_are_consumed_in_order(game_state_ctx: GameStateContext) -> None:
    behavior = _start_dialog_script(
        game_state_ctx,
        [
            DialogTurn(message_id=1, reply=ByReplyId(reply_id=10)),
            DialogTurn(message_id=2, reply=ByReplyId(reply_id=20), finish_after=True),
        ],
    )
    resolve_reply = _resolve_reply_of(behavior)

    first = resolve_reply(_make_question(1, [10, 11]))
    second = resolve_reply(_make_question(2, [20, 21]))

    assert first is not None
    assert first.reply_id == 10
    assert first.do_finish_after is False
    assert second is not None
    assert second.reply_id == 20
    assert second.do_finish_after is True


def test_dialog_turn_without_message_id_matches_any_question(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _start_dialog_script(
        game_state_ctx, [DialogTurn(reply=ByIndex(index=1), finish_after=True)]
    )

    reply_info = _resolve_reply_of(behavior)(_make_question(48366, [10, 11]))

    assert reply_info is not None
    assert reply_info.reply_id == 11


def test_unexpected_question_resolves_to_no_reply(game_state_ctx: GameStateContext) -> None:
    behavior = _start_dialog_script(
        game_state_ctx, [DialogTurn(message_id=1, reply=ByReplyId(reply_id=10))]
    )

    assert _resolve_reply_of(behavior)(_make_question(999, [10])) is None


def test_npc_not_on_map_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [TalkToNpcStep(bones_id=1901, turns=[])]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.NPC_NOT_FOUND]
