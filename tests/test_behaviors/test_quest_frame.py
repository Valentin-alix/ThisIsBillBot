from threading import Event

from DBDofusUnity.datas.protos.non_obf.game.quest_pb2 import (
    QuestsEvent,
    QuestStepStartedEvent,
    QuestValidatedEvent,
)

from src.core.events_manager.event_manager import EventManager
from src.core.frames.quest_frame import QuestFrame
from tests.fixtures.game_state import GameStateContext

QUEST_ID = 2510
OBJECTIVE_ID = 77


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
    assert QUEST_ID in quest_state.active_quest_by_id


def test_current_step_id_is_none_for_unknown_quest(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)

    event_manager.process_msg(_make_quests_event(step_id=3))

    assert game_state_ctx.game_state.quest.current_step_id(4242) is None


def test_step_started_event_updates_current_step(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    event_manager.process_msg(_make_quests_event(step_id=3))

    event_manager.process_msg(QuestStepStartedEvent(quest_id=QUEST_ID, step_id=4))

    assert game_state_ctx.game_state.quest.current_step_id(QUEST_ID) == 4


def test_quest_validated_event_drops_quest_and_counts_it(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    event_manager.process_msg(_make_quests_event(step_id=3))

    event_manager.process_msg(QuestValidatedEvent(quest_id=QUEST_ID))

    quest_state = game_state_ctx.game_state.quest
    assert QUEST_ID not in quest_state.active_quest_by_id
    assert quest_state.current_step_id(QUEST_ID) is None
    assert quest_state.is_finished(QUEST_ID)


def test_disconnection_clears_quest_state(game_state_ctx: GameStateContext) -> None:
    _, event_manager = _make_quest_frame(game_state_ctx)
    event_manager.process_msg(_make_quests_event(step_id=3))

    game_state_ctx.game_info_signals.disconnected.emit()

    assert game_state_ctx.game_state.quest.active_quest_by_id == {}
    assert game_state_ctx.game_state.quest.finished_count_by_quest_id == {}
