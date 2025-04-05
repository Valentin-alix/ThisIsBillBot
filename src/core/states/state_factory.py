from src.core.signals.grid_signals import GridSignals
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.states.craft_state import CraftState
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.game_state import GameState
from src.core.states.guild_chest_state import GuildChestState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.core.states.sale_hotel_state import SaleHotelState
from src.services.logging_utils.loggers import BotLogger


class StateFactory:
    @staticmethod
    def create_game_state(
        inventory_signals: InventorySignals,
        game_info_signals: GameInfoSignals,
        grid_signals: GridSignals,
        logger: BotLogger,
        login: str,
    ):
        player_state = PlayerState(
            game_info_signals=game_info_signals, _logger=logger, login=login
        )
        entity_state = EntityState(
            grid_signals=grid_signals, _logger=logger, player_state=player_state
        )
        inventory_state = InventoryState(
            inventory_signals=inventory_signals,
            _logger=logger,
            player_state=player_state,
        )
        map_state = MapState(
            grid_signals=grid_signals,
            game_info_signals=game_info_signals,
            _logger=logger,
            player_state=player_state,
            entity_state=entity_state,
        )
        sale_hotel_state = SaleHotelState(
            game_info_signals=game_info_signals,
            _logger=logger,
            player_state=player_state,
        )

        fight_state = FightState(
            game_info_signals=game_info_signals,
            player_state=player_state,
            _logger=logger,
            entity_state=entity_state,
        )
        guild_chest_state = GuildChestState(
            game_info_signals=game_info_signals,
            _logger=logger,
            player_state=player_state,
        )
        interactive_state = InteractiveState(
            grid_signals=grid_signals,
            _logger=logger,
            player_state=player_state,
            map_state=map_state,
        )
        craft_state = CraftState(_logger=logger, player_state=player_state)
        game_state = GameState(
            entity=entity_state,
            fight=fight_state,
            inventory=inventory_state,
            interactive=interactive_state,
            map=map_state,
            player=player_state,
            guild_chest=guild_chest_state,
            sale_hotel=sale_hotel_state,
            craft=craft_state,
        )
        return game_state
