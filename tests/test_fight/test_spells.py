from src.core.data_center.data_reader import DataReader
from src.core.logic.fight.effect import get_life_point_malus
from tests.setup_factory import GameStateFixture


class TestSpells(GameStateFixture):
    def test_malus_life_point(self):
        spell_id = 12755  # Déchainement (sacrieur)
        spell_lvl = DataReader().spell_lvl_by_spell_id[spell_id][0]
        life_point_malus = get_life_point_malus(1000, spell_id, spell_lvl.effects[0])
        assert life_point_malus == 100
