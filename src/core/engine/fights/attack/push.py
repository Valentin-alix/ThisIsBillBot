from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint


def _sign(value: int) -> int:
    return (value > 0) - (value < 0)


def _is_blocked(mp: MapPoint, map_id: int, occupied_cell_ids: set[int]) -> bool:
    if mp.cell_id in occupied_cell_ids:
        return True
    cell = MapReader().get_cell_data_by_cell_id(map_id, mp.cell_id)
    return not cell.mov or bool(cell.nonWalkableDuringFight)


def estimate_collision_damage(
    caster_mp: MapPoint,
    enemy_mp: MapPoint,
    push_distance: int,
    map_id: int,
    occupied_cell_ids: set[int],
    player_level: int,
    push_damage_bonus: int,
) -> int:
    """Estimate the collision damage of pushing an enemy away from the caster.

    The enemy is stepped along the dominant caster->enemy grid axis up to
    ``push_distance`` cells; every cell it is prevented from entering (map edge,
    non-walkable cell, or occupied by a fighter) counts as a blocked cell. Mirrors
    PushUtils.GetCollisionDamage with resistance 0:
    ``blocked * (level // 2 + 32 + push_damage_bonus) // 4``.
    """
    dx = enemy_mp.x - caster_mp.x
    dy = enemy_mp.y - caster_mp.y
    if dx == 0 and dy == 0:
        return 0
    step_x, step_y = (_sign(dx), 0) if abs(dx) >= abs(dy) else (0, _sign(dy))

    moved = 0
    current = enemy_mp
    for _ in range(push_distance):
        nxt = MAP_POINT_BY_COORD.get((current.x + step_x, current.y + step_y))
        if nxt is None or _is_blocked(nxt, map_id, occupied_cell_ids):
            break
        current = nxt
        moved += 1

    blocked = push_distance - moved
    if blocked <= 0:
        return 0
    return blocked * (player_level // 2 + 32 + push_damage_bonus) // 4
