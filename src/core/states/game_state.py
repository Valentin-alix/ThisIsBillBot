from dataclasses import dataclass

from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.guild_chest_state import GuildChestState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.party_state import PartyState
from src.core.states.player_state import PlayerState
from src.core.states.sale_hotel_state import SaleHotelState
from src.core.states.server_state import ServerState


@dataclass
class GameState:
    entity: EntityState
    fight: FightState
    interactive: InteractiveState
    inventory: InventoryState
    map: MapState
    objective: ObjectiveState
    player: PlayerState
    party: PartyState
    guild_chest: GuildChestState
    sale_hotel: SaleHotelState
    server: ServerState
