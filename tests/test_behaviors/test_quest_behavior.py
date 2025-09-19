from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

from src.core.behaviors.quests.quest_behavior import QuestBehavior
from src.core.engine.quests.quest_script import (
    GoToStep,
    QuestCooldown,
    QuestScript,
    QuestStep,
)
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext

QUEST_ID = 1199  # startCriterion 'PL>9': no quest prerequisite
DEPENDENT_QUEST_ID = 1200  # startCriterion 'PL>9&Qf=1199&PZ=1'
MAP_IDS = {200}


def _make_behavior(game_state_ctx: GameStateContext) -> QuestBehavior:
    game_state_ctx.game_state.player.level = 200
    behavior = QuestBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        quest_script_behavior=MagicMock(),
    )

    def run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time
        func()

    behavior.run_timer = run_timer_inline
    return behavior


def _make_script(cooldown: QuestCooldown, level_min: int = 1, quest_id: int = QUEST_ID) -> QuestScript:
    steps: list[QuestStep] = [GoToStep(map_ids=MAP_IDS)]
    return QuestScript(name="demo", quest_id=quest_id, cooldown=cooldown, level_min=level_min, steps=steps)


def _started_scripts(behavior: QuestBehavior) -> list[QuestScript]:
    mock = cast(MagicMock, behavior.quest_script_behavior)
    return [call.kwargs["script"] for call in mock.start.call_args_list]


def test_a_one_shot_quest_already_done_is_skipped(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.quest.finished_count_by_quest_id[QUEST_ID] = 1

    behavior.start(scripts=[_make_script(QuestCooldown.NONE)], callback=None, parent=None)

    assert _started_scripts(behavior) == []
    assert not behavior.activity_performed


def test_a_one_shot_quest_never_done_still_runs(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    script = _make_script(QuestCooldown.NONE)

    behavior.start(scripts=[script], callback=None, parent=None)

    assert _started_scripts(behavior) == [script]
    assert behavior.activity_performed


def test_a_daily_quest_runs_again_once_done(game_state_ctx: GameStateContext) -> None:
    """The server resets a daily on its own, so a past completion says nothing about today."""
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.quest.finished_count_by_quest_id[QUEST_ID] = 12
    script = _make_script(QuestCooldown.DAILY)

    behavior.start(scripts=[script], callback=None, parent=None)

    assert _started_scripts(behavior) == [script]


def test_a_quest_above_the_character_level_is_skipped(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.player.level = 10

    behavior.start(scripts=[_make_script(QuestCooldown.DAILY, level_min=50)], callback=None, parent=None)

    assert _started_scripts(behavior) == []


def test_a_failing_script_does_not_abort_the_run(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    first, second = _make_script(QuestCooldown.DAILY), _make_script(QuestCooldown.DAILY)

    behavior.start(scripts=[first, second], callback=None, parent=None)
    mock = cast(MagicMock, behavior.quest_script_behavior)
    mock.start.call_args.kwargs["callback"]("npc_not_found")

    assert _started_scripts(behavior) == [first, second]


def test_a_quest_whose_prerequisite_is_unfinished_is_skipped(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = _make_behavior(game_state_ctx)
    script = _make_script(QuestCooldown.DAILY, quest_id=DEPENDENT_QUEST_ID)

    behavior.start(scripts=[script], callback=None, parent=None)

    assert _started_scripts(behavior) == []


def test_a_quest_whose_prerequisite_is_done_runs(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.quest.finished_count_by_quest_id[QUEST_ID] = 1
    script = _make_script(QuestCooldown.DAILY, quest_id=DEPENDENT_QUEST_ID)

    behavior.start(scripts=[script], callback=None, parent=None)

    assert _started_scripts(behavior) == [script]


def test_a_script_unlocks_the_next_one_within_the_same_run(
    game_state_ctx: GameStateContext,
) -> None:
    """Eligibility is re-checked per script, so finishing a prerequisite unlocks its dependent."""
    behavior = _make_behavior(game_state_ctx)
    prerequisite = _make_script(QuestCooldown.NONE, quest_id=QUEST_ID)
    dependent = _make_script(QuestCooldown.DAILY, quest_id=DEPENDENT_QUEST_ID)

    behavior.start(scripts=[prerequisite, dependent], callback=None, parent=None)
    assert _started_scripts(behavior) == [prerequisite]

    game_state_ctx.game_state.quest.finished_count_by_quest_id[QUEST_ID] = 1
    cast(MagicMock, behavior.quest_script_behavior).start.call_args.kwargs["callback"](None)

    assert _started_scripts(behavior) == [prerequisite, dependent]


def test_a_weekly_quest_runs_again_once_done(game_state_ctx: GameStateContext) -> None:
    behavior = _make_behavior(game_state_ctx)
    game_state_ctx.game_state.quest.finished_count_by_quest_id[QUEST_ID] = 3
    script = _make_script(QuestCooldown.WEEKLY)

    behavior.start(scripts=[script], callback=None, parent=None)

    assert _started_scripts(behavior) == [script]
