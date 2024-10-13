import timeit

from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from tests.setup_factory import GameStateFixture


class TestAttacker(GameStateFixture):
    def test_best_attack(self):
        self.set_game_state(player_cell_id=200, enemy_cell_ids=[180, 400, 250])
        best_attack = self.attacker.find_best_attack_from_mp()
        assert best_attack is not None

    def test_los_attack(self):
        self.set_game_state(
            player_cell_id=119,
            enemy_cell_ids=[243],
            include_spell_ids=[13064],
            map_id=54155586,
            movement_point=5,
        )
        print(I18N.name_by_id[DataReader().spell_by_id[13064].nameId])
        best_attack = self.attacker.find_best_attack_from_mp()
        assert best_attack is None

    def test_benchmark(self):
        self.set_game_state(player_cell_id=200, enemy_cell_ids=[180, 400, 250])
        total_time = timeit.timeit(self.attacker.find_best_attack_from_mp, number=1000)
        print(total_time)
