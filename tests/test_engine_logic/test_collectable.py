from collections.abc import Mapping
from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.game.common_pb2 import InteractiveElement, StatedElement
from dofus_unity_reader.game_constants.job import JobEnum
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.interactives.collectable import (
    Collectable,
    get_stated_element_collectable,
)
from tests.fixtures.data import make_skill_data
from tests.fixtures.interactives import make_interactive_element
from tests.fixtures.map_world import (
    make_map_reference,
)


class TestCollectable:
    def test_collectable_is_farmable_checks_skill_level_and_job_type(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._patch_data_reader(
            monkeypatch,
            {
                1: make_skill_data(level_min=20, parent_job_id=JobEnum.PEASANT),
                2: make_skill_data(level_min=20, parent_job_id=-999),
            },
        )

        collectable = Collectable(
            map_id=1,
            interactive_element=make_interactive_element(1),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=1),
            resource_item_id=100,
        )
        invalid_collectable = Collectable(
            map_id=1,
            interactive_element=make_interactive_element(2),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=2),
            resource_item_id=100,
        )

        assert collectable.is_farmable(20)
        assert not collectable.is_farmable(19)
        assert not invalid_collectable.is_farmable(20)

    @pytest.mark.parametrize(
        (
            "stated_element",
            "interactive_elements_by_id",
            "job_level_by_id",
        ),
        [
            (
                StatedElement(element_id=10, state=1),
                {},
                {},
            ),
            (
                StatedElement(element_id=10, state=0),
                {},
                {},
            ),
            (
                StatedElement(element_id=10, state=0),
                {10: make_interactive_element(1, on_current_map=False)},
                {},
            ),
            (
                StatedElement(element_id=10, state=0),
                {10: InteractiveElement(element_id=10, on_current_map=True)},
                {},
            ),
            (
                StatedElement(element_id=10, state=0),
                {10: make_interactive_element(2)},
                {JobEnum.PEASANT: 200},
            ),
            (
                StatedElement(element_id=10, state=0),
                {10: make_interactive_element(3)},
                {JobEnum.PEASANT: 20},
            ),
        ],
    )
    def test_get_stated_element_collectable_returns_none_for_invalid_inputs(
        self,
        monkeypatch: pytest.MonkeyPatch,
        stated_element: StatedElement,
        interactive_elements_by_id: dict[int, InteractiveElement],
        job_level_by_id: dict[int, int],
    ) -> None:
        self._patch_data_reader(
            monkeypatch,
            {
                1: make_skill_data(
                    gathered_resource_item=100,
                    parent_job_id=JobEnum.PEASANT,
                    level_min=1,
                ),
                2: make_skill_data(
                    gathered_resource_item=-1,
                    parent_job_id=JobEnum.PEASANT,
                    level_min=1,
                ),
                3: make_skill_data(
                    gathered_resource_item=100,
                    parent_job_id=JobEnum.PEASANT,
                    level_min=50,
                ),
            },
        )

        assert (
            get_stated_element_collectable(
                stated_element,
                interactive_elements_by_id,
                1,
                job_level_by_id,
            )
            is None
        )

    def test_get_stated_element_collectable_returns_collectable_when_valid(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._patch_data_reader(
            monkeypatch,
            {
                1: make_skill_data(
                    gathered_resource_item=555,
                    parent_job_id=JobEnum.PEASANT,
                    level_min=1,
                ),
            },
        )

        result = get_stated_element_collectable(
            StatedElement(element_id=10, state=0),
            {10: make_interactive_element(1)},
            123,
            {JobEnum.PEASANT: 50},
        )

        assert result is not None
        assert result.map_id == 123
        assert result.resource_item_id == 555

    def test_collectable_mp_returns_map_point(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._patch_map_reader(monkeypatch, element_id=10, cell_id=42)

        collectable = Collectable(
            map_id=1,
            interactive_element=make_interactive_element(1),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=1),
            resource_item_id=100,
        )

        assert collectable.mp == MapPoint.from_cell_id(42)

    def test_collectable_mp_raises_when_cell_id_is_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        self._patch_map_reader(monkeypatch, element_id=10, cell_id=None)

        collectable = Collectable(
            map_id=1,
            interactive_element=make_interactive_element(1),
            skill=InteractiveElement.InteractiveElementSkill(skill_id=1),
            resource_item_id=100,
        )

        with pytest.raises(ValueError):
            _ = collectable.mp

    def _patch_data_reader(
        self,
        monkeypatch: pytest.MonkeyPatch,
        skill_by_id: Mapping[int, object],
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.skill_by_id = skill_by_id

        monkeypatch.setattr(
            "src.core.engine.interactives.collectable.DataReader",
            lambda: mock_data_reader,
        )

    def _patch_map_reader(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        element_id: int,
        cell_id: int | None,
    ) -> None:
        mock_map_reader = MagicMock()
        mock_map_reader.get_ref_data_by_element_id_by_map_id.return_value = {
            element_id: make_map_reference(cell_id),
        }

        monkeypatch.setattr(
            "src.core.engine.interactives.collectable.MapReader",
            lambda: mock_map_reader,
        )
