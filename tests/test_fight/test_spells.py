from data_center.data_reader import DataReader
from src.core.logic.fight.effect import (
    get_life_point_percent_malus,
    get_effect_shield_level_bonus,
)
from tests.setup_factory import GameStateFixture


class TestSpells(GameStateFixture):
    def test_malus_life_point(self):
        spell_id = 12755  # Déchainement (sacrieur)
        spell_lvl = DataReader().spell_lvl_by_spell_id[spell_id][0]
        life_point_malus = get_life_point_percent_malus(1000, spell_lvl.effects[0])
        assert life_point_malus == 100

    def test_bonus_shield(self):
        level = 100

        params: list[dict[str, int]] = [
            {
                "spell_id": 14676,  # Ferveur (iop)
                "value": 50,
            },
            {
                "spell_id": 13133,  # Endurance (iop)
                "value": 75,
            },
            {
                "spell_id": 13142,  # Vertu (iop)
                "value": 300,
            },
        ]
        for param in params:
            related_spell_lvl = DataReader().spell_lvl_by_spell_id[param["spell_id"]][0]
            print(related_spell_lvl.effects)
            assert any(
                get_effect_shield_level_bonus(level, effect) == param["value"]
                for effect in related_spell_lvl.effects
            )
