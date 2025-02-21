from unittest.mock import MagicMock

from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
)
from dofus_unity_reader.enums.monster_gid_enum import MonsterGidEnum
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.monsters.monster_group import (
    get_level_monster_group,
    get_monster_groups,
    is_valid_monster_group,
)
from tests.fixtures.entities import (
    make_actor,
    make_monster_actor,
    make_monster_group_actor,
)


class TestMonsterGroup:
    def test_get_level_monster_group_sums_main_creature_and_underlings(
        self,
    ) -> None:
        monster_group = make_monster_group_actor(1, 12, [(2, 7), (3, 9)])

        assert get_level_monster_group(monster_group) == 28

    def test_get_monster_groups_returns_only_monster_groups(
        self,
    ) -> None:
        monster_group = make_monster_group_actor(1, 12)

        actor_by_id: dict[int, ActorPositionInformation] = {
            1: make_monster_actor(1, 42, monster_group),
            2: make_actor(actor_id=2, cell_id=43),
        }

        result = get_monster_groups(actor_by_id)

        assert result == [(1, MapPoint.from_cell_id(42), monster_group)]

    def test_is_valid_monster_group_rejects_forbidden_monsters(
        self,
    ) -> None:
        game_state = MagicMock()
        monster_group = make_monster_group_actor(MonsterGidEnum.POUTCH, 1)

        assert not is_valid_monster_group(game_state, monster_group, 1, 10)

    def test_is_valid_monster_group_accepts_equal_level_limit(
        self,
    ) -> None:
        game_state = MagicMock()
        monster_group = make_monster_group_actor(1, 10)

        assert is_valid_monster_group(game_state, monster_group, 20, 20)
        assert not is_valid_monster_group(game_state, monster_group, 21, 20)
