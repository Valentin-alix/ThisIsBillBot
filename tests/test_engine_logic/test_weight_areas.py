from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from DBDofusUnity.dofus_unity_reader.data_center.area_info import AreaInfo

from src.core.engine.contexts import HarvesterAreaContext
from src.core.engine.weights import weight_areas


def test_area_selection_scores_accessible_harvestables_without_map_scan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    accessible_area = AreaInfo(area_id=1, sub_area_id=10)
    inaccessible_area = AreaInfo(area_id=2, sub_area_id=20, min_lvl=201)
    data_reader = SimpleNamespace(
        sub_area_by_id={10: SimpleNamespace(harvestables=[100])},
        sub_areas_by_area_id={1: [10]},
    )
    collectable_weight = MagicMock(return_value=10.0)
    map_weight = MagicMock(side_effect=AssertionError("area selection must not read maps"))

    monkeypatch.setattr(weight_areas, "AREAS_SUB_WITH_WEIGHT", [accessible_area, inaccessible_area])
    monkeypatch.setattr(weight_areas, "DataReader", lambda: data_reader)
    monkeypatch.setattr(
        weight_areas,
        "GameDataController",
        lambda: SimpleNamespace(get_item_job_by_gfx=lambda: {1: (100, 5)}),
    )
    monkeypatch.setattr(weight_areas, "get_weight_collectable", collectable_weight)
    monkeypatch.setattr(weight_areas, "get_map_id_collectable_weight", map_weight)

    result = weight_areas.get_random_best_area_info(
        old_area_id=None,
        old_sub_area_id=None,
        context=HarvesterAreaContext(
            player_level=200,
            player_waypoint_map_ids=frozenset(),
            player_is_sub=True,
            player_server_id=1,
            player_jobs_lvl_by_id={5: 200},
            bank_storage_by_gid={},
            current_area_infos_by_server_and_character={},
        ),
        previous_area_info_played=[],
        logger=MagicMock(),
    )

    assert result == accessible_area
    collectable_weight.assert_called_once()
    map_weight.assert_not_called()
