from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.core.engine.movements.area_infos import AreaInfo
from src.core.engine.weights.harvester.weight_areas import (
    get_random_best_area_info_for_harvester,
    is_valid_area_info_to_harvest,
)
from tests.setup_factory import GameStateFixture


class TestWeightAreas(GameStateFixture):
    def setUp(self) -> None:
        super().setUp()
        self.game_state.player.level = 100
        self.game_state.player.waypoint_map_ids = []
        self.game_state.player.subscription_end_date = datetime.now() + timedelta(
            days=1
        )
        self.game_state.player.jobs_lvl_by_id = {}
        self.game_state.player.server_id = 1
        self.game_state.inventory.bank_object_by_gid = {}

    def test_is_valid_area_info_to_harvest_applies_all_filters(self) -> None:
        area_info = AreaInfo(
            area_id=1, sub_area_id=2, min_lvl=50, waypoint_id_needed=99
        )
        self.game_state.player.level = 60
        self.game_state.player.waypoint_map_ids = [99]
        weight_by_area = {area_info: 10.0}

        self.assertTrue(
            is_valid_area_info_to_harvest(area_info, self.game_state, weight_by_area)
        )

        self.game_state.player.level = 49
        self.assertFalse(
            is_valid_area_info_to_harvest(area_info, self.game_state, weight_by_area)
        )
        self.game_state.player.level = 60
        self.game_state.player.waypoint_map_ids = []
        self.assertFalse(
            is_valid_area_info_to_harvest(area_info, self.game_state, weight_by_area)
        )
        self.game_state.player.waypoint_map_ids = [99]
        weight_by_area[area_info] = 0
        self.assertFalse(
            is_valid_area_info_to_harvest(area_info, self.game_state, weight_by_area)
        )

    def test_get_random_best_area_info_for_harvester_returns_old_area_when_present(
        self,
    ) -> None:
        result = get_random_best_area_info_for_harvester(
            old_area_id=10,
            old_sub_area_id=20,
            game_state=self.game_state,
            previous_area_info_played=[],
            logger=MagicMock(),
        )

        self.assertEqual(result, AreaInfo(area_id=10, sub_area_id=20))

    def test_get_random_best_area_info_for_harvester_applies_penalties_and_weights(
        self,
    ) -> None:
        logger = MagicMock()
        self.game_state.player.waypoint_map_ids = [777]
        area_one = AreaInfo(area_id=1)
        area_two = AreaInfo(area_id=2, sub_area_id=22, waypoint_id_needed=777)
        with (
            patch(
                "src.core.engine.weights.harvester.weight_areas.AREAS_SUB_WITH_WEIGHT",
                [area_one, area_two],
            ),
            patch(
                "src.core.engine.weights.harvester.weight_areas.get_weight_harvester_area"
            ) as mock_get_area_weight,
            patch(
                "src.core.engine.weights.harvester.weight_areas.get_weight_harvester_sub_area"
            ) as mock_get_sub_area_weight,
            patch(
                "src.core.engine.weights.harvester.weight_areas.random.choices"
            ) as mock_random_choices,
            patch.dict(
                "src.core.engine.weights.harvester.weight_areas.CURRENT_AREAS_PLAYING_INFOS_BY_SERVER_AND_CHARACTER",
                {(1, 123): area_one},
                clear=True,
            ),
        ):

            def get_area_weight(
                _job_lvl_by_id: dict[int, int],
                _area_id: int,
                _is_sub: bool,
                _storage_by_gid: dict[int, object],
                _server_id: int = 1,
            ) -> int:
                return 100

            def get_sub_area_weight(
                _job_lvl_by_id: dict[int, int],
                _storage_by_gid: dict[int, object],
                _sub_area_id: int,
                _is_sub: bool,
                _server_id: int = 1,
            ) -> int:
                return 100

            mock_get_area_weight.side_effect = get_area_weight
            mock_get_sub_area_weight.side_effect = get_sub_area_weight
            mock_random_choices.return_value = [area_two]
            result = get_random_best_area_info_for_harvester(
                old_area_id=None,
                old_sub_area_id=None,
                game_state=self.game_state,
                previous_area_info_played=[area_one],
                logger=logger,
            )

        self.assertEqual(result, area_two)
        self.assertEqual(mock_random_choices.call_args.kwargs["weights"], [20.0, 100.0])
        self.assertEqual(mock_random_choices.call_args.args[0], [area_one, area_two])
