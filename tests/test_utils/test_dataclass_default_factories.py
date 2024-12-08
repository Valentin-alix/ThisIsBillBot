import unittest

from src.core.engine.fights.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.engine.movements.map.map_data_adapter import DataMapProvider
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.events_manager.event_manager import EventManager
from src.core.events_manager.subject import Subject
from src.core.signals.grid_signals import GridSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.states.game_state import GameState
from src.core.states.state_factory import StateFactory
from src.services.logging.logger import Logger


def create_game_state_fixture() -> tuple[GameState, Logger]:
    logger = Logger(log_signals=LogSignals(), title="dataclass-default-factories")
    game_state = StateFactory.create_game_state(
        inventory_signals=InventorySignals(),
        game_info_signals=GameInfoSignals(),
        grid_signals=GridSignals(),
        logger=logger,
    )
    return game_state, logger


class TestDataclassDefaultFactories(unittest.TestCase):
    def test_pathfinding_collections_are_not_shared_between_instances(self) -> None:
        game_state, logger = create_game_state_fixture()
        self.addCleanup(logger.close)
        pathfinding = Pathfinding(
            data_map_provider=DataMapProvider(game_state=game_state),
            game_state=game_state,
            logger=logger,
        )
        other_pathfinding = Pathfinding(
            data_map_provider=DataMapProvider(game_state=game_state),
            game_state=game_state,
            logger=logger,
        )

        assert pathfinding.node_by_coord is not other_pathfinding.node_by_coord
        assert pathfinding.open_list is not other_pathfinding.open_list
        assert pathfinding.is_coord_closed is not other_pathfinding.is_coord_closed
        assert pathfinding.occupied_cell_ids is not other_pathfinding.occupied_cell_ids
        assert pathfinding.end_columns is not other_pathfinding.end_columns
        assert pathfinding.end_lines is not other_pathfinding.end_lines
        assert pathfinding.end_x_coords is not other_pathfinding.end_x_coords
        assert pathfinding.end_y_coords is not other_pathfinding.end_y_coords

    def test_fight_reachable_cells_collections_are_not_shared_between_instances(
        self,
    ) -> None:
        game_state, logger = create_game_state_fixture()
        self.addCleanup(logger.close)
        fight_reachable_cells = FightReachableCells(game_state=game_state)
        other_reachable_cells = FightReachableCells(game_state=game_state)

        assert (
            fight_reachable_cells.reachable_cost_by_mp
            is not other_reachable_cells.reachable_cost_by_mp
        )
        assert fight_reachable_cells.node_by_mp is not other_reachable_cells.node_by_mp
        assert fight_reachable_cells.open_node is not other_reachable_cells.open_node

    def test_event_manager_collections_are_not_shared_between_instances(self) -> None:
        logger = Logger(log_signals=LogSignals(), title="event-manager-test")
        self.addCleanup(logger.close)
        event_manager = EventManager(_logger=logger)
        other_event_manager = EventManager(_logger=logger)

        assert (
            event_manager.modifier_by_type_msg
            is not other_event_manager.modifier_by_type_msg
        )
        assert (
            event_manager.listeners_by_type_msg
            is not other_event_manager.listeners_by_type_msg
        )

    def test_subject_observers_are_not_shared_between_instances(self) -> None:
        subject = Subject()
        other_subject = Subject()

        assert subject._observers is not other_subject._observers


if __name__ == "__main__":
    unittest.main()
