from src.core.engine.quests.quest_criterion import get_required_finished_quest_ids

SCENE_DE_MENAGE_QUEST_ID = 1199
BIEN_VELU_QUEST_ID = 1200  # startCriterion: PL>9&Qf=1199&PZ=1


def test_a_required_quest_is_read_from_the_criterion() -> None:
    assert get_required_finished_quest_ids(BIEN_VELU_QUEST_ID) == {SCENE_DE_MENAGE_QUEST_ID}


def test_a_quest_without_prerequisite_requires_nothing() -> None:
    assert get_required_finished_quest_ids(SCENE_DE_MENAGE_QUEST_ID) == frozenset()


def test_an_unknown_quest_requires_nothing() -> None:
    assert get_required_finished_quest_ids(999_999) == frozenset()


def test_every_registered_quest_criterion_is_readable() -> None:
    """Guard against a criterion shape the splitter would choke on."""
    from dofus_unity_reader.data_center.data_reader import DataReader

    for quest_id in DataReader().quest_by_id:
        get_required_finished_quest_ids(quest_id)
