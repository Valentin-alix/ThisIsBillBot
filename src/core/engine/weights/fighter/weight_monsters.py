from dataclasses import dataclass

from src.core.engine.movements.map.path_finding.movement_path import MovementPath


@dataclass
class MonsterGroupToAttack:
    actor_id: int
    move_path: MovementPath
    level: int


def get_weight_monster_group_grp_to_attack(
    monster_group_to_attack: MonsterGroupToAttack,
    inventory_weight: int,
    inventory_weight_max: int,
) -> float:
    duration_move = MovementPath.get_total_duration(
        monster_group_to_attack.move_path.path,
        inventory_weight,
        inventory_weight_max,
    )
    return (1 + monster_group_to_attack.level) / (1 + duration_move**2)
