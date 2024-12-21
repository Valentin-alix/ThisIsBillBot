import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dofus_unity_reader.models.datas.dungeons_root import DungeonsRootItem
from datas.protos.non_obf.game.common_pb2 import (
    ObjectEffect,
    ObjectItem,
    ObjectItemInventory,
)

from src.core.engine.dungeons.dungeon_access import (
    do_have_key_access_to_dungeon,
    get_valid_dungeon_infos,
)
from src.core.engine.dungeons.dungeon_info import DungeonInfo
from src.core.engine.items.item_type import ItemTypeEnum
from src.core.game_constants import Items


def _make_dungeon_info(
    name: str,
    key_name: str,
    optimal_level: int,
    entrance_map_id: int,
) -> DungeonInfo:
    dungeon_info = DungeonInfo.__new__(DungeonInfo)
    dungeon_info.name = name
    dungeon_info.key_name = key_name
    dungeon_info.dungeon = DungeonsRootItem(
        id=entrance_map_id,
        nameId=0,
        optimalPlayerLevel=optimal_level,
        mapIds=[1, 2, 3],
        entranceMapId=entrance_map_id,
        exitMapId=entrance_map_id + 1,
    )
    return dungeon_info


class TestDungeonAccess(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = MagicMock()
        self.dungeon_info = _make_dungeon_info("Test Dungeon", "clef du test", 30, 123)

    @patch("src.core.engine.dungeons.dungeon_access.I18N")
    @patch("src.core.engine.dungeons.dungeon_access.DataReader")
    def test_do_have_key_access_to_dungeon_returns_true_when_key_is_in_key_ring(
        self,
        mock_data_reader_class: MagicMock,
        mock_i18n_class: MagicMock,
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.item_by_id = {
            10: SimpleNamespace(id=10, nameId=1, typeId=ItemTypeEnum.KEY),
            11: SimpleNamespace(id=11, nameId=2, typeId=ItemTypeEnum.KEY),
        }
        mock_data_reader_class.return_value = mock_data_reader

        mock_i18n = MagicMock()
        mock_i18n.name_by_id = {1: "clef du test", 2: "Autre clef"}
        mock_i18n_class.return_value = mock_i18n

        objects_by_uid: dict[int, ObjectItemInventory] = {
            1: ObjectItemInventory(
                item=ObjectItem(
                    gid=Items.KEY_RING,
                    effects=[ObjectEffect(value_int=10)],
                )
            )
        }

        self.assertTrue(
            do_have_key_access_to_dungeon(
                self.dungeon_info, objects_by_uid, self.logger
            )
        )

    @patch("src.core.engine.dungeons.dungeon_access.I18N")
    @patch("src.core.engine.dungeons.dungeon_access.DataReader")
    def test_do_have_key_access_to_dungeon_returns_false_when_related_key_is_missing(
        self,
        mock_data_reader_class: MagicMock,
        mock_i18n_class: MagicMock,
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.item_by_id = {
            11: SimpleNamespace(id=11, nameId=2, typeId=ItemTypeEnum.KEY),
        }
        mock_data_reader_class.return_value = mock_data_reader

        mock_i18n = MagicMock()
        mock_i18n.name_by_id = {2: "Autre clef"}
        mock_i18n_class.return_value = mock_i18n

        objects_by_uid: dict[int, ObjectItemInventory] = {
            1: ObjectItemInventory(item=ObjectItem(gid=Items.KEY_RING))
        }

        self.assertFalse(
            do_have_key_access_to_dungeon(
                self.dungeon_info, objects_by_uid, self.logger
            )
        )
        self.logger.error.assert_called_once()

    def test_do_have_key_access_to_dungeon_raises_when_key_ring_is_missing(
        self,
    ) -> None:
        with self.assertRaises(StopIteration):
            do_have_key_access_to_dungeon(self.dungeon_info, {}, self.logger)

    def test_get_valid_dungeon_infos_filters_by_level_sub_and_key_access(self) -> None:
        accessible = _make_dungeon_info("Accessible", "a", 20, 1000)
        blocked_for_unsub = _make_dungeon_info("Blocked", "b", 20, 1001)
        too_high = _make_dungeon_info("TooHigh", "c", 45, 1002)
        no_key = _make_dungeon_info("NoKey", "d", 20, 1003)

        with (
            patch(
                "src.core.engine.dungeons.dungeon_access.Dungeons.ALL",
                [accessible, blocked_for_unsub, too_high, no_key],
            ),
            patch("src.core.engine.dungeons.dungeon_access.DUNGEON_OFFSET_LVL", 10),
            patch(
                "src.core.engine.dungeons.dungeon_access.MapTools.is_map_allowed_for_unsub"
            ) as mock_is_map_allowed,
            patch(
                "src.core.engine.dungeons.dungeon_access.do_have_key_access_to_dungeon"
            ) as mock_has_key_access,
        ):

            def is_map_allowed(map_id: int) -> bool:
                return map_id != 1001

            def has_key_access(
                info: DungeonInfo,
                _objects_by_uid: dict[int, ObjectItemInventory],
                _logger: MagicMock,
            ) -> bool:
                return info.name != "NoKey"

            mock_is_map_allowed.side_effect = is_map_allowed
            mock_has_key_access.side_effect = has_key_access
            result = get_valid_dungeon_infos(
                level=50,
                is_sub=False,
                objects_by_uid={},
                logger=self.logger,
            )

        self.assertEqual(result, [accessible])
