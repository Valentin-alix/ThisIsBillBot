from datas.protos.non_obf.game.common_pb2 import ActorPositionInformation

from src.core.engine.monsters.monster_group import get_monster_group_gids

MonsterGroupActor = ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor

XELOR_LOUCHE_MONSTER_ID = 3363
TOFU_MONSTER_ID = 98


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
