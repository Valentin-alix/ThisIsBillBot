from typing import NamedTuple

from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.contexts import AttackContext, FightReachableContext
from src.core.engine.fights.reachable_cells.fight_reachable_cells import FightReachableCells


class AttackPositions(NamedTuple):
    entities_mp: set[MapPoint]
    entities_id_by_mp: dict[MapPoint, int]
    enemies_mp: set[MapPoint]


def get_positions(context: AttackContext) -> AttackPositions:
    entities_id_by_mp: dict[MapPoint, int] = {
        MapPoint.from_cell_id(actor.disposition.cell_id): actor.actor_id
        for actor in context.actor_by_id.values()
        if actor.disposition.cell_id != -1
    }
    entities_mp = set(entities_id_by_mp.keys())
    enemies_mp = {MapPoint.from_cell_id(enemy.disposition.cell_id) for enemy in context.enemy_actors}
    return AttackPositions(
        entities_mp=entities_mp,
        entities_id_by_mp=entities_id_by_mp,
        enemies_mp=enemies_mp,
    )


def get_movable_mps(
    context: AttackContext,
    positions: AttackPositions,
    fight_reachable_cells: FightReachableCells,
) -> dict[MapPoint, int]:
    invisible_enemy_mps = {MapPoint.from_cell_id(cell_id) for cell_id in context.invisible_enemy_cell_ids}
    movable_mps = fight_reachable_cells.search(
        FightReachableContext(
            map_id=context.map_id,
            player_map_point=context.player_map_point,
            movement_points=context.movement_points,
        ),
        enemies_mp=positions.enemies_mp,
        entities_mp=positions.entities_mp | invisible_enemy_mps,
    )
    movable_mps[context.player_map_point] = context.movement_points
    return movable_mps
