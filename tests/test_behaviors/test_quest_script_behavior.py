from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    InteractiveElement,
    ObjectItem,
    ObjectItemInventory,
)
from DBDofusUnity.datas.protos.non_obf.game.context_pb2 import ContextCreationEvent
from DBDofusUnity.datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent
from DBDofusUnity.datas.protos.non_obf.game.quest_pb2 import QuestActive, QuestValidatedEvent
from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.game_constants.map_id import MapIdEnum
from DBDofusUnity.dofus_unity_reader.game_constants.npc import NpcDialogInfo
from DBDofusUnity.dofus_unity_reader.game_constants.skill import SkillEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.craft.craft_behavior import CraftRequest
from src.core.behaviors.quests.quest_script_behavior import (
    QuestScriptBehavior,
    QuestScriptError,
)
from src.core.engine.npcs.dialog_turn import DialogTurn
from DBDofusUnity.dofus_unity_reader.game_constants.world import WorldMapEnum

from src.core.engine.quests.quest_script import (
    BuyItemStep,
    CraftItemStep,
    EnsureItemStep,
    FightStep,
    GoToStep,
    QuestScript,
    QuestStep,
    TalkToNpcStep,
    UseMapInteractiveStep,
)
from src.core.behaviors.items.acquire_items_behavior import ItemToAcquire
from src.core.engine.npcs.reply_selector import ByReplyId
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext

QUEST_ID = 2510
NPC_ID = 1901
START_MAP_ID = 100
DESTINATION_MAP_ID = 200
DESTINATION_MAP_IDS = {DESTINATION_MAP_ID}
OTHER_MAP_IDS = {300}
OBJECTIVE_A = 6752
OBJECTIVE_B = 6753


KERUBIM_SHOP_CLOSED_MESSAGE_ID = 12877
KERUBIM_LISTEN_MESSAGE_ID = 13470
KERUBIM_HELP_REPLY_ID = 15482
KERUBIM_LISTEN_REPLY_ID = 15483
SNORI_NAIRB_NPC_ID = 1088
XELOR_LOUCHE_MONSTER_ID = 3363
CIRE_DE_GLIGLI_GID = 14508
GRAISSE_GELATINEUSE_GID = 1983
POILS_DE_KERUBIM_GID = 13608
PREPARER_POTION_SKILL_ID = 23
POLISH_SKILL_ID = 700
SHELF_CELL_IDS = (314, 347)


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
        fight_behavior=MagicMock(),
        interactive_behavior=MagicMock(),
        acquire_items_behavior=MagicMock(),
        craft_behavior=MagicMock(),
    )

    def run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time
        func()

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
    _arrive(behavior, DESTINATION_MAP_ID)

    _mock_of(behavior.attacker_behavior).start.assert_called_once()
    assert _child_kwarg(behavior.attacker_behavior, "count_fight_limit") == 2
    assert finished == []

    _child_callback(behavior.attacker_behavior)(None, 2)

    assert finished == [None]


def test_fight_step_targets_the_quest_monster(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.map.map_id = DESTINATION_MAP_ID
    steps: list[QuestStep] = [
        FightStep(map_ids=DESTINATION_MAP_IDS, monster_id=3363, count=1, wait_for_group=False)
    ]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _child_kwarg(behavior.attacker_behavior, "monster_ids") == {3363}
    assert _child_kwarg(behavior.attacker_behavior, "wait_for_group") is False


def test_fight_step_without_monster_id_does_not_filter(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.map.map_id = DESTINATION_MAP_ID
    steps: list[QuestStep] = [FightStep(map_ids=DESTINATION_MAP_IDS)]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _child_kwarg(behavior.attacker_behavior, "monster_ids") is None


def test_unfought_quest_monster_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.map.map_id = DESTINATION_MAP_ID
    steps: list[QuestStep] = [
        FightStep(map_ids=DESTINATION_MAP_IDS, monster_id=3363, count=1, wait_for_group=False)
    ]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)
    _child_callback(behavior.attacker_behavior)(None, 0)

    assert finished == [QuestScriptError.FIGHT_NOT_COMPLETED]


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

    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == DESTINATION_MAP_IDS


def _declare_objective(game_state_ctx: GameStateContext, objective_id: int, done: bool = False) -> None:
    quest = game_state_ctx.game_state.quest.active_quest_by_id.setdefault(
        QUEST_ID, QuestActive(quest_id=QUEST_ID)
    )
    objective = quest.details.objectives.add()
    objective.objective_id = objective_id
    objective.objective_reached = not done


def _objective_script(steps: list[QuestStep]) -> QuestScript:
    return QuestScript(
        name="demo",
        quest_id=QUEST_ID,
        steps=steps,
        objective_id_by_index={1: OBJECTIVE_A, 2: OBJECTIVE_B},
    )


def test_an_already_accepted_quest_skips_the_step_that_takes_it(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _declare_objective(game_state_ctx, OBJECTIVE_A)
    steps: list[QuestStep] = [
        TalkToNpcStep(npc_id=NPC_ID, turns=[]),
        GoToStep(map_ids=OTHER_MAP_IDS),
        GoToStep(map_ids=DESTINATION_MAP_IDS),
    ]

    _start(behavior, _objective_script(steps))

    _mock_of(behavior.npc_dialog_behavior).start.assert_not_called()
    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == OTHER_MAP_IDS


def test_a_quest_not_yet_accepted_starts_at_the_first_step(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [
        TalkToNpcStep(npc_id=NPC_ID, turns=[]),
        GoToStep(map_ids=OTHER_MAP_IDS),
        GoToStep(map_ids=DESTINATION_MAP_IDS),
    ]

    _start(behavior, _objective_script(steps))

    _mock_of(behavior.npc_dialog_behavior).start.assert_called_once()


def test_resume_skips_every_objective_already_reached(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _declare_objective(game_state_ctx, OBJECTIVE_A, done=True)
    _declare_objective(game_state_ctx, OBJECTIVE_B)
    steps: list[QuestStep] = [
        TalkToNpcStep(npc_id=NPC_ID, turns=[]),
        GoToStep(map_ids=OTHER_MAP_IDS),
        GoToStep(map_ids=DESTINATION_MAP_IDS),
    ]

    _start(behavior, _objective_script(steps))

    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == DESTINATION_MAP_IDS


def test_an_objective_reached_mid_run_skips_its_step(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    _declare_objective(game_state_ctx, OBJECTIVE_A)
    _declare_objective(game_state_ctx, OBJECTIVE_B)
    steps: list[QuestStep] = [
        TalkToNpcStep(npc_id=NPC_ID, turns=[]),
        GoToStep(map_ids=OTHER_MAP_IDS),
        GoToStep(map_ids=DESTINATION_MAP_IDS),
    ]
    finished: list[str | None] = []

    _start(behavior, _objective_script(steps), finished)

    game_state_ctx.game_state.quest.mark_objective_reached(QUEST_ID, OBJECTIVE_B)
    _arrive(behavior, next(iter(OTHER_MAP_IDS)))

    assert finished == [None]
    assert _mock_of(behavior.auto_trip_smart_behavior).start.call_count == 1


def test_script_starts_at_zero_when_server_step_is_unmapped(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.quest.set_current_step_id(QUEST_ID, 999)
    steps: list[QuestStep] = [GoToStep(map_ids=OTHER_MAP_IDS), FightStep()]

    _start(
        behavior,
        QuestScript(name="demo", quest_id=QUEST_ID, steps=steps, server_step_id_by_index={0: 55}),
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


def _make_question(message_id: int, reply_ids: list[int]) -> NpcDialogQuestionEvent:
    msg = NpcDialogQuestionEvent(message_id=message_id)
    for reply_id in reply_ids:
        msg.visible_replies.add().reply_id = reply_id
    return msg


def test_declared_turns_are_handed_to_the_dialog_behavior(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    turns = [DialogTurn(reply=ByReplyId(reply_id=10), finish_after=True)]
    steps: list[QuestStep] = [TalkToNpcStep(npc_id=NPC_ID, turns=turns)]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _child_kwarg(behavior.npc_dialog_behavior, "turn_variants") == [turns]


def test_npc_not_on_map_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [TalkToNpcStep(bones_id=1901, turns=[])]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.NPC_NOT_FOUND]


def _put_npc_on_map(behavior: QuestScriptBehavior, npc_id: int, actor_id: int) -> None:
    actor = ActorPositionInformation(actor_id=actor_id)
    actor.actor_information.role_play_actor.npc_actor.npc_id = npc_id
    behavior.game_state.entity.actor_by_id[actor_id] = actor


def _resolved_npc_id(behavior: QuestScriptBehavior) -> int:
    npc_dialog_info = _child_kwarg(behavior.npc_dialog_behavior, "npc_dialog_info")
    assert isinstance(npc_dialog_info, NpcDialogInfo)
    return behavior.game_state.entity.resolve_npc_id(npc_dialog_info)


def test_npc_name_resolves_against_the_npc_standing_on_the_map(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _put_npc_on_map(behavior, npc_id=SNORI_NAIRB_NPC_ID, actor_id=SNORI_NAIRB_NPC_ID)
    steps: list[QuestStep] = [TalkToNpcStep(npc_name="Snori Nairb", turns=[])]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _resolved_npc_id(behavior) == SNORI_NAIRB_NPC_ID


def test_a_shared_npc_name_is_resolved_by_the_map(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    _put_npc_on_map(behavior, npc_id=NPC_ID, actor_id=NPC_ID)
    steps: list[QuestStep] = [TalkToNpcStep(npc_name="Kerubim Crepin", turns=[])]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _resolved_npc_id(behavior) == NPC_ID


def test_a_named_npc_absent_from_the_map_aborts_the_script(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [TalkToNpcStep(npc_name="Snori Nairb", turns=[])]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.NPC_NOT_FOUND]
    _mock_of(behavior.npc_dialog_behavior).start.assert_not_called()


def test_an_unknown_npc_name_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [TalkToNpcStep(npc_name="Kerubim Crepine", turns=[])]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.NPC_NOT_FOUND]


def test_monster_name_is_resolved_into_the_targeting_filter(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.map.map_id = DESTINATION_MAP_ID
    steps: list[QuestStep] = [FightStep(map_ids=DESTINATION_MAP_IDS, monster_name="Xelor Louche", count=1)]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _child_kwarg(behavior.attacker_behavior, "monster_ids") == {XELOR_LOUCHE_MONSTER_ID}


def test_an_unknown_monster_name_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.map.map_id = DESTINATION_MAP_ID
    steps: list[QuestStep] = [FightStep(map_ids=DESTINATION_MAP_IDS, monster_name="Xelor Absent")]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.UNKNOWN_MONSTER]
    _mock_of(behavior.attacker_behavior).start.assert_not_called()


def test_coord_and_world_are_resolved_into_travel_destinations(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [GoToStep(coord=(7, -19))]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == {188746755}


def test_map_name_narrows_an_interior_destination(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [
        GoToStep(coord=(6, -18), world=WorldMapEnum.INTERIOR, map_name="Taverne d'Astrub - Chambre du pirate")
    ]

    _start(behavior, QuestScript(name="demo", steps=steps))

    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == {192416768}


def test_a_pending_objective_is_not_taken_for_a_done_one(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _declare_objective(game_state_ctx, OBJECTIVE_A)
    _declare_objective(game_state_ctx, OBJECTIVE_B)
    steps: list[QuestStep] = [
        TalkToNpcStep(npc_id=NPC_ID, turns=[]),
        GoToStep(map_ids=OTHER_MAP_IDS),
        GoToStep(map_ids=DESTINATION_MAP_IDS),
    ]

    _start(behavior, _objective_script(steps))

    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == OTHER_MAP_IDS


def test_an_objective_absent_from_the_server_is_not_done(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _declare_objective(game_state_ctx, OBJECTIVE_A, done=True)
    steps: list[QuestStep] = [
        TalkToNpcStep(npc_id=NPC_ID, turns=[]),
        GoToStep(map_ids=OTHER_MAP_IDS),
        GoToStep(map_ids=DESTINATION_MAP_IDS),
    ]

    _start(behavior, _objective_script(steps))

    assert _child_kwarg(behavior.auto_trip_smart_behavior, "map_ids") == DESTINATION_MAP_IDS


def _enter_fight(behavior: QuestScriptBehavior) -> None:
    behavior.game_state.fight.in_fight = True
    behavior.event_manager.process_msg(ContextCreationEvent(context=ContextCreationEvent.GameContext.FIGHT))


def test_a_fight_started_by_an_npc_is_played_before_resuming(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [
        TalkToNpcStep(npc_id=NPC_ID, turns=[]),
        GoToStep(map_ids=DESTINATION_MAP_IDS),
    ]

    _start(behavior, QuestScript(name="demo", steps=steps))
    _enter_fight(behavior)

    _mock_of(behavior.fight_behavior).start.assert_called_once()


def test_no_travel_is_attempted_while_in_fight(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [GoToStep(map_ids=DESTINATION_MAP_IDS)]
    game_state_ctx.game_state.fight.in_fight = True

    _start(behavior, QuestScript(name="demo", steps=steps))

    _mock_of(behavior.auto_trip_smart_behavior).start.assert_not_called()


def test_the_step_resumes_once_the_fight_is_over(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [GoToStep(map_ids=DESTINATION_MAP_IDS)]

    _start(behavior, QuestScript(name="demo", steps=steps))
    _enter_fight(behavior)
    behavior.game_state.fight.in_fight = False
    _child_callback(behavior.fight_behavior)(None)

    _mock_of(behavior.auto_trip_smart_behavior).start.assert_called()


def _put_interactives_on_map(behavior: QuestScriptBehavior, map_id: int, skill_id: int) -> None:
    behavior.game_state.map.map_id = map_id
    behavior.game_state.interactive.interactive_element_by_id.clear()
    for element_id in MapReader().get_ref_data_by_element_id_by_map_id(map_id):
        behavior.game_state.interactive.interactive_element_by_id[element_id] = InteractiveElement(
            element_id=element_id,
            on_current_map=True,
            enabled_skills=[InteractiveElement.InteractiveElementSkill(skill_id=skill_id)],
        )


def test_use_map_interactive_takes_a_furniture_not_an_exit(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    _put_interactives_on_map(behavior, MapIdEnum.KERUBIM_SHOP, POLISH_SKILL_ID)
    steps: list[QuestStep] = [UseMapInteractiveStep(map_ids={MapIdEnum.KERUBIM_SHOP})]

    _start(behavior, QuestScript(name="demo", steps=steps))

    element_mp = cast(MapPoint, _child_kwarg(behavior.interactive_behavior, "element_mp"))
    assert element_mp.cell_id == SHELF_CELL_IDS[0]


def test_two_use_map_interactive_steps_take_two_different_furnitures(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _put_interactives_on_map(behavior, MapIdEnum.KERUBIM_SHOP, POLISH_SKILL_ID)
    steps: list[QuestStep] = [
        UseMapInteractiveStep(map_ids={MapIdEnum.KERUBIM_SHOP}),
        UseMapInteractiveStep(map_ids={MapIdEnum.KERUBIM_SHOP}),
    ]

    _start(behavior, QuestScript(name="demo", steps=steps))
    used_element_id = cast(int, _child_kwarg(behavior.interactive_behavior, "element_id"))
    behavior.game_state.interactive.interactive_element_by_id[used_element_id] = InteractiveElement(
        element_id=used_element_id, on_current_map=True
    )
    _child_callback(behavior.interactive_behavior)(None)

    element_mp = cast(MapPoint, _child_kwarg(behavior.interactive_behavior, "element_mp"))
    assert element_mp.cell_id == SHELF_CELL_IDS[1]


def test_use_map_interactive_without_candidate_aborts_the_script(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _put_interactives_on_map(behavior, MapIdEnum.KERUBIM_SHOP, SkillEnum.EXIT)
    steps: list[QuestStep] = [UseMapInteractiveStep(map_ids={MapIdEnum.KERUBIM_SHOP})]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.INTERACTIVE_NOT_FOUND]
    _mock_of(behavior.interactive_behavior).start.assert_not_called()


def test_craft_item_step_crafts_from_the_inventory(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [CraftItemStep(item_gid=CIRE_DE_GLIGLI_GID, quantity=2)]

    _start(behavior, QuestScript(name="demo", steps=steps))

    craft_requests = cast(list[CraftRequest], _child_kwarg(behavior.craft_behavior, "craft_requests"))
    assert [req.recipe.resultId for req in craft_requests] == [CIRE_DE_GLIGLI_GID]
    assert craft_requests[0].recipe.skillId == PREPARER_POTION_SKILL_ID
    assert craft_requests[0].stop_condition == 2


def test_craft_item_step_without_recipe_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [CraftItemStep(item_gid=-1)]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)

    assert finished == [QuestScriptError.UNKNOWN_RECIPE]


def _put_in_inventory(behavior: QuestScriptBehavior, item_gid: int, quantity: int) -> None:
    behavior.game_state.inventory.objects_by_uid[item_gid] = ObjectItemInventory(
        item=ObjectItem(uid=item_gid, gid=item_gid, quantity=quantity)
    )


def test_buy_item_step_delegates_the_whole_need_to_the_sourcing_behavior(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    _put_in_inventory(behavior, GRAISSE_GELATINEUSE_GID, 2)
    steps: list[QuestStep] = [BuyItemStep(item_gid=GRAISSE_GELATINEUSE_GID, max_kamas=5_000, quantity=5)]

    _start(behavior, QuestScript(name="demo", steps=steps))

    items = cast(list[ItemToAcquire], _child_kwarg(behavior.acquire_items_behavior, "items"))
    assert [(item.item_gid, item.quantity, item.max_kamas) for item in items] == [
        (GRAISSE_GELATINEUSE_GID, 5, 5_000)
    ]


def test_buy_item_step_passes_when_nothing_was_missing(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    _put_in_inventory(behavior, POILS_DE_KERUBIM_GID, 1)
    steps: list[QuestStep] = [BuyItemStep(item_gid=POILS_DE_KERUBIM_GID, max_kamas=50_000)]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)
    _child_callback(behavior.acquire_items_behavior)(None, {})

    assert finished == [None]


def test_a_partial_sourcing_aborts_the_script(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    steps: list[QuestStep] = [BuyItemStep(item_gid=GRAISSE_GELATINEUSE_GID, max_kamas=5_000, quantity=5)]
    finished: list[str | None] = []

    _start(behavior, QuestScript(name="demo", steps=steps), finished)
    _put_in_inventory(behavior, GRAISSE_GELATINEUSE_GID, 4)
    _child_callback(behavior.acquire_items_behavior)(None, {GRAISSE_GELATINEUSE_GID: 1})

    assert finished == [QuestScriptError.ITEM_MISSING]
