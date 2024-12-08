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
    def test_weight_is_the_primary_tie_breaker(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
        )
        cases = [
            ("higher_weight", 15.0, 3, 200, current_best, True),
            ("lower_weight", 5.0, 3, 200, current_best, False),
            (
                "weight_beats_remaining_pm",
                15.0,
                2,
                200,
                cast(
                    tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
                    (10.0, 5, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
                ),
                True,
            ),
            (
                "weight_beats_distance",
                15.0,
                3,
                102,
                cast(
                    tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
                    (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(110)),
                ),
                True,
            ),
        ]

        for name, weight, remaining_pm, target_cell_id, best_so_far, expected in cases:
            with self.subTest(case=name):
                is_better = self.attacker._is_better_attack(
                    weight=weight,
                    remaining_pm=remaining_pm,
                    from_mp=MapPoint.from_cell_id(100),
                    target_mp=MapPoint.from_cell_id(target_cell_id),
                    current_best=best_so_far,
                )

                assert is_better is expected

    def test_remaining_pm_breaks_weight_ties_before_distance(self):
        current_best = cast(
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
            (10.0, 3, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(200)),
        )
        cases = [
            ("more_remaining_pm", 4, 200, current_best, True),
            ("less_remaining_pm", 2, 200, current_best, False),
            (
                "remaining_pm_beats_distance",
                4,
                102,
                cast(
                    tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
                    (10.0, 2, MapPoint.from_cell_id(100), None, MapPoint.from_cell_id(110)),
                ),
                True,
            ),
        ]

        for name, remaining_pm, target_cell_id, best_so_far, expected in cases:
            with self.subTest(case=name):
                is_better = self.attacker._is_better_attack(
                    weight=10.0,
                    remaining_pm=remaining_pm,
                    from_mp=MapPoint.from_cell_id(100),
                    target_mp=MapPoint.from_cell_id(target_cell_id),
                    current_best=best_so_far,
                )

                assert is_better is expected

    def test_distance_breaks_final_ties(self):
        cases = [
            ("farther_is_better", 102, 105, True),
            ("closer_is_worse", 105, 102, False),
            ("same_distance_keeps_current", 105, 105, False),
        ]

        for name, current_target_cell_id, candidate_target_cell_id, expected in cases:
            with self.subTest(case=name):
                current_best = cast(
                    tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
                    (
                        10.0,
                        3,
                        MapPoint.from_cell_id(100),
                        None,
                        MapPoint.from_cell_id(current_target_cell_id),
                    ),
                )

                is_better = self.attacker._is_better_attack(
                    weight=10.0,
                    remaining_pm=3,
                    from_mp=MapPoint.from_cell_id(100),
                    target_mp=MapPoint.from_cell_id(candidate_target_cell_id),
                    current_best=current_best,
                )

                assert is_better is expected


class TestAttackPositioning(GameStateFixture):
    def test_detailed_attack_positions(self):
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
