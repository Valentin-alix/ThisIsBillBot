import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dofus_unity_reader.enums.jobs_enum import JobEnum
from dofus_unity_reader.grid.map_point import MapPoint
from datas.protos.non_obf.game.common_pb2 import InteractiveElement, StatedElement

from src.core.engine.interactives.collectable import (
    Collectable,
    get_stated_element_collectable,
)


class TestCollectable(unittest.TestCase):
    @staticmethod
    def _make_interactive_element(
        skill_id: int, on_current_map: bool = True
    ) -> InteractiveElement:
        return InteractiveElement(
            element_id=10,
            on_current_map=on_current_map,
            enabled_skills=[
                InteractiveElement.InteractiveElementSkill(skill_id=skill_id)
            ],
        )

    @patch("src.core.engine.interactives.collectable.DataReader")
    def test_collectable_is_farmable_checks_skill_level_and_job_type(
        self, mock_data_reader_class: MagicMock
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.skill_by_id = {
            1: SimpleNamespace(levelMin=20, parentJobId=JobEnum.PEASANT),
            2: SimpleNamespace(levelMin=20, parentJobId=-999),
        }
        mock_data_reader_class.return_value = mock_data_reader

        collectable = Collectable(
            map_id=1,
            interactive_element=self._make_interactive_element(1),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=1),
            resource_item_id=100,
        )
        invalid_collectable = Collectable(
            map_id=1,
            interactive_element=self._make_interactive_element(2),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=2),
            resource_item_id=100,
        )

        self.assertTrue(collectable.is_farmable(20))
        self.assertFalse(collectable.is_farmable(19))
        self.assertFalse(invalid_collectable.is_farmable(20))

    @patch("src.core.engine.interactives.collectable.DataReader")
    def test_get_stated_element_collectable_filters_invalid_inputs(
        self, mock_data_reader_class: MagicMock
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.skill_by_id = {
            1: SimpleNamespace(
                gatheredRessourceItem=100, parentJobId=JobEnum.PEASANT, levelMin=1
            ),
            2: SimpleNamespace(
                gatheredRessourceItem=-1, parentJobId=JobEnum.PEASANT, levelMin=1
            ),
            3: SimpleNamespace(
                gatheredRessourceItem=100, parentJobId=JobEnum.PEASANT, levelMin=50
            ),
        }
        mock_data_reader_class.return_value = mock_data_reader

        stated_element = StatedElement(element_id=10, state=0)

        self.assertIsNone(
            get_stated_element_collectable(
                StatedElement(element_id=10, state=1), {}, 1, {}
            )
        )
        self.assertIsNone(get_stated_element_collectable(stated_element, {}, 1, {}))
        self.assertIsNone(
            get_stated_element_collectable(
                stated_element,
                {10: self._make_interactive_element(1, on_current_map=False)},
                1,
                {},
            )
        )
        self.assertIsNone(
            get_stated_element_collectable(
                stated_element,
                {10: InteractiveElement(element_id=10, on_current_map=True)},
                1,
                {},
            )
        )
        self.assertIsNone(
            get_stated_element_collectable(
                stated_element,
                {10: self._make_interactive_element(2)},
                1,
                {JobEnum.PEASANT: 200},
            )
        )
        self.assertIsNone(
            get_stated_element_collectable(
                stated_element,
                {10: self._make_interactive_element(3)},
                1,
                {JobEnum.PEASANT: 20},
            )
        )

    @patch("src.core.engine.interactives.collectable.DataReader")
    def test_get_stated_element_collectable_returns_collectable_when_valid(
        self, mock_data_reader_class: MagicMock
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.skill_by_id = {
            1: SimpleNamespace(
                gatheredRessourceItem=555, parentJobId=JobEnum.PEASANT, levelMin=1
            ),
        }
        mock_data_reader_class.return_value = mock_data_reader

        result = get_stated_element_collectable(
            StatedElement(element_id=10, state=0),
            {10: self._make_interactive_element(1)},
            123,
            {JobEnum.PEASANT: 50},
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.map_id, 123)
        self.assertEqual(result.resource_item_id, 555)

    @patch("src.core.engine.interactives.collectable.MapReader")
    def test_collectable_mp_returns_map_point(
        self, mock_map_reader_class: MagicMock
    ) -> None:
        mock_map_reader = MagicMock()
        mock_map_reader.get_ref_data_by_element_id_by_map_id.return_value = {
            10: SimpleNamespace(cellId=42)
        }
        mock_map_reader_class.return_value = mock_map_reader

        collectable = Collectable(
            map_id=1,
            interactive_element=self._make_interactive_element(1),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=1),
            resource_item_id=100,
        )

        self.assertEqual(collectable.mp, MapPoint.from_cell_id(42))

    @patch("src.core.engine.interactives.collectable.MapReader")
    def test_collectable_mp_raises_when_cell_id_is_missing(
        self, mock_map_reader_class: MagicMock
    ) -> None:
        mock_map_reader = MagicMock()
        mock_map_reader.get_ref_data_by_element_id_by_map_id.return_value = {
            10: SimpleNamespace(cellId=None)
        }
        mock_map_reader_class.return_value = mock_map_reader

        collectable = Collectable(
            map_id=1,
            interactive_element=self._make_interactive_element(1),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=1),
            resource_item_id=100,
        )

        with self.assertRaises(ValueError):
            _ = collectable.mp
