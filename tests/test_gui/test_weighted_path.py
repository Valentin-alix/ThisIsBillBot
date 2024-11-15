from timeit import timeit

from data_center.data_reader import DataReader
from enums.area_enum import SubAreaEnum

from tests.fixtures.random_generator import (
    generate_random_bot,
)
from tests.setup_factory import GameStateFixture
from tests.test_gui.simulator import simulate_weighted_path


class TestWeightedPath(GameStateFixture):
    def test_weighted_path(self):
        bot = generate_random_bot()

        map_id = next(
            iter(DataReader().map_ids_by_sub_area_id[SubAreaEnum.ASTRUB_CITY])
        )

        self.set_game_state(player_cell_id=200, enemy_cell_ids=[], map_id=map_id)

        bot.game_state = self.game_state

        time = timeit(lambda: simulate_weighted_path(bot), number=10)
        print(time)
