from typing import cast

from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem
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
        best_attack = self.attacker.find_best_attack_from_mp()
        assert best_attack is None


class TestIsBetterAttack(GameStateFixture):
    def test_higher_weight_is_better(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
        )

        is_better = self.attacker._is_better_attack(
            weight=15.0,
            remaining_pm=3,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(200),
            current_best=current_best,
        )

        assert is_better is True

    def test_lower_weight_is_worse(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
        )

        is_better = self.attacker._is_better_attack(
            weight=5.0,
            remaining_pm=3,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(200),
            current_best=current_best,
        )

        assert is_better is False

    def test_same_weight_more_remaining_pm_is_better(self):
        """Plus de PM restants = meilleur (moins utilisé de PM pour se déplacer)"""
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
        )

        is_better = self.attacker._is_better_attack(
            weight=10.0,
            remaining_pm=4,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(200),
            current_best=current_best,
        )

        assert is_better is True

    def test_same_weight_less_remaining_pm_is_worse(self):
        """Moins de PM restants = pire (plus utilisé de PM pour se déplacer)"""
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
        )

        is_better = self.attacker._is_better_attack(
            weight=10.0,
            remaining_pm=2,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(200),
            current_best=current_best,
        )

        assert is_better is False

    def test_same_weight_same_pm_farther_distance_is_better(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(102)),
        )

        is_better = self.attacker._is_better_attack(
            weight=10.0,
            remaining_pm=3,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(105),
            current_best=current_best,
        )

        assert is_better is True

    def test_same_weight_same_pm_closer_distance_is_worse(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(105)),
        )

        is_better = self.attacker._is_better_attack(
            weight=10.0,
            remaining_pm=3,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(102),
            current_best=current_best,
        )

        assert is_better is False

    def test_same_weight_same_pm_same_distance_keeps_current(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(105)),
        )

        is_better = self.attacker._is_better_attack(
            weight=10.0,
            remaining_pm=3,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(105),
            current_best=current_best,
        )

        assert is_better is False

    def test_priority_weight_over_pm_remaining(self):
        """Un meilleur weight est prioritaire même si moins de PM restants"""
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 5, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
        )

        is_better = self.attacker._is_better_attack(
            weight=15.0,
            remaining_pm=2,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(200),
            current_best=current_best,
        )

        assert is_better is True

    def test_priority_weight_over_distance(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(110)),
        )

        is_better = self.attacker._is_better_attack(
            weight=15.0,
            remaining_pm=3,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(102),
            current_best=current_best,
        )

        assert is_better is True

    def test_priority_pm_remaining_over_distance(self):
        """Plus de PM restants est prioritaire sur la distance"""
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 2, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(110)),
        )

        is_better = self.attacker._is_better_attack(
            weight=10.0,
            remaining_pm=4,
            from_mp=MapPoint.from_cell_id(100),
            target_mp=MapPoint.from_cell_id(102),
            current_best=current_best,
        )

        assert is_better is True


class TestAttackPositioning(GameStateFixture):
    def test_detailed_attack_positions(self):
        """Test détaillé pour voir toutes les positions possibles"""
        self.set_game_state(
            player_cell_id=100,
            enemy_cell_ids=[150],
            movement_point=5,
        )

        movable_mps = self.attacker.fight_reachable_cells.search(
            enemies_mp={MapPoint.from_cell_id(150)},
            entities_mp={MapPoint.from_cell_id(100), MapPoint.from_cell_id(150)},
        )
        movable_mps[self.game_state.map.map_point] = 5

        best_attack = self.attacker.find_best_attack_from_mp()
        if best_attack:
            from_mp, spell_lvl, target_mp = best_attack
            pm_used = 5 - movable_mps.get(from_mp, 0)

            assert pm_used <= 0, (
                f"Bot should stay at current position (100) but moved to {from_mp.cell_id}"
            )
