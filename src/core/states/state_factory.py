from src.common.logger import Logger
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.game_state import GameState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals


class StateFactory:
    @staticmethod
    def create_game_state(
        game_info_signals: GameInfoSignals, grid_signals: GridSignals, logger: Logger
    ):
        entity_state = EntityState(grid_signals=grid_signals, logger=logger)
        interactive_state = InteractiveState(grid_signals=grid_signals, logger=logger)
        inventory_state = InventoryState(
            game_info_signals=game_info_signals, logger=logger
        )
        map_state = MapState(grid_signals=grid_signals, logger=logger)

        player_state = PlayerState(
            game_info_signals=game_info_signals,
            map_state=map_state,
            interactive_state=interactive_state,
            entity_state=entity_state,
            logger=logger,
        )
        fight_state = FightState(
            game_info_signals=game_info_signals,
            player_state=player_state,
            logger=logger,
        )

        objective_state = ObjectiveState(logger=logger)

        game_state = GameState(
            entity=entity_state,
            fight=fight_state,
            inventory=inventory_state,
            interactive=interactive_state,
            map=map_state,
            player=player_state,
            objective=objective_state,
        )
        return game_state
