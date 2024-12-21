import unittest
from unittest.mock import MagicMock

from dofus_unity_reader.enums.monster_gid_enum import MonsterGidEnum
from dofus_unity_reader.grid.map_point import MapPoint
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)

from src.core.engine.monsters.monster_group import (
    get_level_monster_group,
    get_monster_groups,
    is_valid_monster_group,
)


def _make_monster_group_actor(
    main_gid: int,
    main_level: int,
    underlings: list[tuple[int, int]] | None = None,
) -> ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor:
    monster_group = (
        ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor()
    )
    monster_group.identification.main_creature.gid = main_gid
    monster_group.identification.main_creature.level = main_level
    for underling_gid, underling_level in underlings or []:
        underling = monster_group.identification.underlings.add()
        underling.gid = underling_gid
        underling.level = underling_level
    return monster_group


def _make_monster_actor(
    actor_id: int,
    cell_id: int,
    monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
) -> ActorPositionInformation:
    return ActorPositionInformation(
        actor_id=actor_id,
        disposition=EntityDisposition(cell_id=cell_id),
        actor_information=ActorPositionInformation.ActorInformation(
            role_play_actor=ActorPositionInformation.ActorInformation.RolePlayActor(
                monster_group_actor=monster_group
            )
        ),
    )


class TestMonsterGroup(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = MagicMock()

    def test_get_level_monster_group_sums_main_creature_and_underlings(self) -> None:
        monster_group = _make_monster_group_actor(1, 12, [(2, 7), (3, 9)])

        self.assertEqual(get_level_monster_group(monster_group), 28)

    def test_get_monster_groups_returns_only_monster_groups(self) -> None:
        monster_group = _make_monster_group_actor(1, 12)
        actor_by_id: dict[int, ActorPositionInformation] = {
            1: _make_monster_actor(1, 42, monster_group),
            2: ActorPositionInformation(
                actor_id=2,
                disposition=EntityDisposition(cell_id=43),
            ),
        }

        result = get_monster_groups(actor_by_id)

        self.assertEqual(result, [(1, MapPoint.from_cell_id(42), monster_group)])

    def test_is_valid_monster_group_rejects_forbidden_monsters(self) -> None:
        monster_group = _make_monster_group_actor(MonsterGidEnum.POUTCH, 1)

        self.assertFalse(is_valid_monster_group(self.logger, monster_group, 1, 10))

    def test_is_valid_monster_group_accepts_equal_level_limit(self) -> None:
        monster_group = _make_monster_group_actor(1, 10)

        self.assertTrue(is_valid_monster_group(self.logger, monster_group, 20, 20))
        self.assertFalse(is_valid_monster_group(self.logger, monster_group, 21, 20))
