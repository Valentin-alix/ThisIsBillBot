from src.core.engine.movements.map.map_data_adapter import DataMapProvider
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.services.logging.logger import Logger
from tests.test_e2e.e2e_test_base import E2ETestBase
from tests.test_e2e.validators.movement_validator import MovementValidator


class TestMovementE2E(E2ETestBase):
    def setUp(self):
        super().setUp()
        logger = Logger(log_signals=self.bot.log_signals, title="")
        data_map_provider = DataMapProvider(game_state=self.game_state)
        self.pathfinding = Pathfinding(
            data_map_provider=data_map_provider,
            game_state=self.game_state,
            logger=logger,
        )

    def test_movement_timing_matches_calculation(self):
        path = self.load_recording("movement_session")

        validator = MovementValidator(
            character_id=self.game_state.player.character_id,
            inventory_weight=self.game_state.inventory.inventory_weight,
            inventory_weight_max=self.game_state.inventory.weight_max,
            pathfinding=self.pathfinding,
            timing_tolerance_ms=50,
        )
        self.register_validator(validator)

        self.assert_recording_valid(path)

    def test_key_cells_consistency(self):
        path = self.load_recording("movement_session")

        validator = MovementValidator(
            character_id=self.game_state.player.character_id,
            inventory_weight=self.game_state.inventory.inventory_weight,
            inventory_weight_max=self.game_state.inventory.weight_max,
            pathfinding=self.pathfinding,
        )
        self.register_validator(validator)

        self.assert_recording_valid(path)
