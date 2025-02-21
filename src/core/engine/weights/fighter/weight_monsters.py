from dataclasses import dataclass

from src.core.engine.movements.map.path_finding.movement_path import MovementPath


@dataclass
class MonsterGroupInfo:
    actor_id: int
    move_path: MovementPath
    level: int


def get_weight_monster_group_info(
    monster_group_info: MonsterGroupInfo,
    inventory_weight: int,
    inventory_weight_max: int,
) -> float:
    duration_move = MovementPath.get_total_duration(
        monster_group_info.move_path.path,
        inventory_weight,
        inventory_weight_max,
    )
    return (1 + monster_group_info.level) / (1 + duration_move**2)
