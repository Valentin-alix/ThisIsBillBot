from dataclasses import dataclass

from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


@dataclass
class GameState:
    entity: EntityState
    fight: FightState
    interactive: InteractiveState
    inventory: InventoryState
    map: MapState
    objective: ObjectiveState
    player: PlayerState
