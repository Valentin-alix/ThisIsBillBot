from dataclasses import dataclass

from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.states.game_state import GameState


@dataclass
class MonsterGroupInfo:
    actor_id: int
    move_path: MovementPath
    level: int


def get_weight_monster_group_info(
    monster_group_info: MonsterGroupInfo, game_state: GameState
) -> float:
    duration_move = MovementPath.get_total_duration(
        monster_group_info.move_path.path,
        game_state.inventory.inventory_weight,
        game_state.inventory.weight_max,
    )
    return (1 + monster_group_info.level) / (1 + duration_move**2)
