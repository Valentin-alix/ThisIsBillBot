from src.common.logger import Logger
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.game_state import GameState
from src.core.states.guild_chest_state import GuildChestState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.core.states.sale_hotel_state import SaleHotelState
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals, InventorySignals


class StateFactory:
    @staticmethod
    def create_game_state(
        inventory_signals: InventorySignals,
        game_info_signals: GameInfoSignals,
        grid_signals: GridSignals,
        logger: Logger,
    ):
        entity_state = EntityState(grid_signals=grid_signals, logger=logger)
        inventory_state = InventoryState(
            inventory_signals=inventory_signals, logger=logger
        )
        map_state = MapState(
            grid_signals=grid_signals,
            game_info_signals=game_info_signals,
            logger=logger,
        )
        sale_hotel_state = SaleHotelState(
            game_info_signals=game_info_signals, logger=logger
        )
        player_state = PlayerState(
            game_info_signals=game_info_signals,
            map_state=map_state,
            entity_state=entity_state,
            logger=logger,
            sale_hotel_state=sale_hotel_state,
        )
        fight_state = FightState(
            game_info_signals=game_info_signals,
            player_state=player_state,
            logger=logger,
        )
        guild_chest_state = GuildChestState(
            game_info_signals=game_info_signals, logger=logger
        )
        interactive_state = InteractiveState(
            grid_signals=grid_signals,
            logger=logger,
            player_state=player_state,
            map_state=map_state,
        )

        game_state = GameState(
            entity=entity_state,
            fight=fight_state,
            inventory=inventory_state,
            interactive=interactive_state,
            map=map_state,
            player=player_state,
            guild_chest=guild_chest_state,
            sale_hotel=sale_hotel_state,
        )
        return game_state
