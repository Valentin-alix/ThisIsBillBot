from tests.setup_factory import GameStateFixture


class TestEntities(GameStateFixture):
    def test_is_entity_on_cell_id(self):
        player_cell_id = 300
        self.set_game_state(player_cell_id, [])
        assert self.game_state.entity.actors_on_mp.is_entity_actor_on_cell_id(
            player_cell_id
        )
