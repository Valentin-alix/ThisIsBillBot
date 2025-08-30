from threading import Event

from datas.protos.non_obf.game.npc_pb2 import NpcsMapQuestStatusUpdateEvent
from datas.protos.non_obf.game.quest_pb2 import (
    QuestObjectiveValidatedEvent,
    QuestsEvent,
    QuestStepStartedEvent,
    QuestValidatedEvent,
)

from src.core.events_manager.event_manager import EventManager
from src.core.frames.quest_frame import QuestFrame
from tests.fixtures.game_state import GameStateContext

QUEST_ID = 2510
OBJECTIVE_ID = 77
NPC_ID = -20001


def _make_quest_frame(game_state_ctx: GameStateContext) -> tuple[QuestFrame, EventManager]:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    frame = QuestFrame(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        _logger=game_state_ctx.logger,
        is_playing_event=Event(),
    )
    return frame, event_manager


def _make_quests_event(step_id: int) -> QuestsEvent:
    msg = QuestsEvent()
    active = msg.active_quests.add()
    active.quest_id = QUEST_ID
    active.details.step_id = step_id
    objective = active.details.objectives.add()
    objective.objective_id = OBJECTIVE_ID
    objective.objective_reached = False
    finished = msg.finished_quests.add()
    finished.quest_id = 99
    finished.finished_count = 4
    return msg


def test_quests_event_fills_active_and_finished_quests(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    quest_state = game_state_ctx.game_state.quest

    event_manager.process_msg(_make_quests_event(step_id=3))

    assert quest_state.current_step_id(QUEST_ID) == 3
    assert quest_state.finished_count_by_quest_id == {99: 4}
    assert quest_state.is_active(QUEST_ID)


def test_current_step_id_is_none_for_unknown_quest(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)

    event_manager.process_msg(_make_quests_event(step_id=3))

    assert game_state_ctx.game_state.quest.current_step_id(4242) is None


def test_step_started_event_updates_current_step(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    event_manager.process_msg(_make_quests_event(step_id=3))

    event_manager.process_msg(QuestStepStartedEvent(quest_id=QUEST_ID, step_id=4))

    assert game_state_ctx.game_state.quest.current_step_id(QUEST_ID) == 4


def test_objective_validated_event_marks_objective_reached(
    game_state_ctx: GameStateContext,
) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    event_manager.process_msg(_make_quests_event(step_id=3))
    quest_state = game_state_ctx.game_state.quest
    assert not quest_state.is_objective_reached(QUEST_ID, OBJECTIVE_ID)

    event_manager.process_msg(
        QuestObjectiveValidatedEvent(quest_id=QUEST_ID, objective_id=OBJECTIVE_ID)
    )

    assert quest_state.is_objective_reached(QUEST_ID, OBJECTIVE_ID)


def test_quest_validated_event_drops_quest_and_counts_it(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    event_manager.process_msg(_make_quests_event(step_id=3))

    event_manager.process_msg(QuestValidatedEvent(quest_id=QUEST_ID))

    quest_state = game_state_ctx.game_state.quest
    assert not quest_state.is_active(QUEST_ID)
    assert quest_state.current_step_id(QUEST_ID) is None
    assert quest_state.finished_count_by_quest_id[QUEST_ID] == 1


def test_npcs_map_quest_status_reports_startable_quests(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    msg = NpcsMapQuestStatusUpdateEvent()
    map_information = msg.map_information.add()
    map_information.map_id = 1234
    npc_with_quest = map_information.npcs_with_quests.add()
    npc_with_quest.npc_id = NPC_ID
    npc_with_quest.quests_to_start.append(QUEST_ID)

    event_manager.process_msg(msg)

    quest_state = game_state_ctx.game_state.quest
    assert quest_state.is_startable_by_npc(NPC_ID, QUEST_ID)
    assert not quest_state.is_startable_by_npc(NPC_ID, 1)
    assert not quest_state.is_validable_by_npc(NPC_ID, QUEST_ID)
    assert quest_state.has_npc_quest_status(NPC_ID)


def test_disconnection_clears_quest_state(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    event_manager.process_msg(_make_quests_event(step_id=3))

    game_state_ctx.game_info_signals.disconnected.emit()

    assert game_state_ctx.game_state.quest.active_quest_by_id == {}
    assert game_state_ctx.game_state.quest.finished_count_by_quest_id == {}
