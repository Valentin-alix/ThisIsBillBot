import pytest
from dofus_unity_reader.data_center.data_reader import DataReader

from src.core.behaviors.quests.quest_script_behavior import get_map_ids_for_coord
from src.core.engine.quests.quest_script import (
    GoToStep,
    QuestScript,
    QuestStep,
    StepWithDestination,
    TalkToNpcStep,
)
from src.core.engine.quests.scripts import QUEST_SCRIPTS


def test_registered_scripts_target_existing_maps() -> None:
    for script in QUEST_SCRIPTS:
        for index, step in enumerate(script.steps):
            if not isinstance(step, StepWithDestination) or step.coord is None:
                continue
            map_ids = get_map_ids_for_coord(step.coord, step.sub_area_id)
            assert map_ids, f"{script.name} step {index}: no map at {step.coord}"


def test_registered_scripts_map_known_quest_and_step_ids() -> None:
    data_reader = DataReader()
    for script in QUEST_SCRIPTS:
        if script.quest_id is None:
            continue
        assert script.quest_id in data_reader.quest_by_id, (
            f"{script.name}: unknown quest id {script.quest_id}"
        )
        for index, step_id in script.server_step_id_by_index.items():
            assert step_id in data_reader.quest_step_by_id, (
                f"{script.name} step {index}: unknown server step id {step_id}"
            )


def test_step_index_outside_the_script_is_rejected() -> None:
    steps: list[QuestStep] = [GoToStep(map_ids={1})]

    with pytest.raises(ValueError, match="outside of its steps"):
        QuestScript(name="ko", steps=steps, server_step_id_by_index={5: 1})


def test_script_without_step_is_rejected() -> None:
    with pytest.raises(ValueError, match="has no step"):
        QuestScript(name="ko", steps=[])


def test_coord_and_map_ids_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        GoToStep(coord=(3, -17), map_ids={1})


def test_sub_area_id_requires_a_coord() -> None:
    with pytest.raises(ValueError, match="only narrows a coord"):
        GoToStep(map_ids={1}, sub_area_id=95)


def test_go_to_needs_a_destination() -> None:
    with pytest.raises(ValueError, match="needs either coord or map_ids"):
        GoToStep()


def test_talk_to_npc_needs_an_npc_identity() -> None:
    with pytest.raises(ValueError, match="needs either npc_id or bones_id"):
        TalkToNpcStep(coord=(3, -17))


def test_sub_area_id_narrows_an_ambiguous_coord() -> None:
    all_map_ids = get_map_ids_for_coord((3, -17))
    narrowed = get_map_ids_for_coord((3, -17), sub_area_id=95)

    assert narrowed
    assert narrowed < all_map_ids
