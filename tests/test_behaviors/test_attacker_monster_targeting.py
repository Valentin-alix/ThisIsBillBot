import logging

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ActorPositionInformation
from DBDofusUnity.dofus_unity_reader.game_constants.monster import MonsterGidEnum

from src.core.engine.monsters.monster_group import get_monster_group_gids, is_group_targetable

MonsterGroupActor = ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor

XELOR_LOUCHE_MONSTER_ID = 3363
TOFU_MONSTER_ID = 98

_LOGGER = logging.getLogger(__name__)


def _make_monster_group(main_gid: int, underling_gids: list[int]) -> MonsterGroupActor:
    monster_group = MonsterGroupActor()
    monster_group.identification.main_creature.gid = main_gid
    for gid in underling_gids:
        monster_group.identification.underlings.add().gid = gid
    return monster_group


def test_group_gids_include_main_creature_and_underlings() -> None:
    monster_group = _make_monster_group(XELOR_LOUCHE_MONSTER_ID, [TOFU_MONSTER_ID, TOFU_MONSTER_ID])

    assert get_monster_group_gids(monster_group) == {XELOR_LOUCHE_MONSTER_ID, TOFU_MONSTER_ID}


def test_group_gids_of_a_lone_monster() -> None:
    monster_group = _make_monster_group(XELOR_LOUCHE_MONSTER_ID, [])

    assert get_monster_group_gids(monster_group) == {XELOR_LOUCHE_MONSTER_ID}


def test_targeting_matches_a_group_containing_the_quest_monster() -> None:
    quest_group = _make_monster_group(XELOR_LOUCHE_MONSTER_ID, [])
    other_group = _make_monster_group(TOFU_MONSTER_ID, [TOFU_MONSTER_ID])
    targeted = {XELOR_LOUCHE_MONSTER_ID}

    assert targeted & get_monster_group_gids(quest_group)
    assert not targeted & get_monster_group_gids(other_group)


def test_targeting_matches_when_the_quest_monster_is_an_underling() -> None:
    monster_group = _make_monster_group(TOFU_MONSTER_ID, [XELOR_LOUCHE_MONSTER_ID])

    assert {XELOR_LOUCHE_MONSTER_ID} & get_monster_group_gids(monster_group)


def test_is_group_targetable_rejects_forbidden_gid() -> None:
    monster_group = _make_monster_group(MonsterGidEnum.POUTCH, [])

    assert not is_group_targetable(_LOGGER, monster_group, 10, lvl_limit=100, monster_ids=None)


def test_is_group_targetable_rejects_when_monster_ids_do_not_match() -> None:
    monster_group = _make_monster_group(TOFU_MONSTER_ID, [])

    assert not is_group_targetable(
        _LOGGER,
        monster_group,
        10,
        lvl_limit=100,
        monster_ids={XELOR_LOUCHE_MONSTER_ID},
    )


def test_is_group_targetable_accepts_when_monster_ids_match() -> None:
    monster_group = _make_monster_group(XELOR_LOUCHE_MONSTER_ID, [])

    assert is_group_targetable(
        _LOGGER,
        monster_group,
        10,
        lvl_limit=100,
        monster_ids={XELOR_LOUCHE_MONSTER_ID},
    )


def test_is_group_targetable_rejects_group_over_lvl_limit() -> None:
    monster_group = _make_monster_group(TOFU_MONSTER_ID, [])

    assert not is_group_targetable(_LOGGER, monster_group, 150, lvl_limit=100, monster_ids=None)


def test_is_group_targetable_accepts_group_within_lvl_limit() -> None:
    monster_group = _make_monster_group(TOFU_MONSTER_ID, [])

    assert is_group_targetable(_LOGGER, monster_group, 100, lvl_limit=100, monster_ids=None)
