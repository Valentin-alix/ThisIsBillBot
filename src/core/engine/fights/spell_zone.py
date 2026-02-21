from utils.cache import cache
from DBDofusUnity.dofus_unity_reader.game_constants.spell_shape_enum import SpellShapeEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.fights.zones.cone import Cone
from src.core.engine.fights.zones.cross import Cross
from src.core.engine.fights.zones.fork import Fork
from src.core.engine.fights.zones.half_lozenge import HalfLozenge
from src.core.engine.fights.zones.line import Line
from src.core.engine.fights.zones.lozenge import Lozenge
from src.core.engine.fights.zones.rectangle import Rectangle
from src.core.engine.fights.zones.square import Square
from src.core.engine.fights.zones.zone import Zone


@cache
def get_zone_mps(
    shape: SpellShapeEnum,
    size: int,
    alternative_size: int,
    caster_mp: MapPoint,
    stop_at_target: bool,
) -> Zone:
    match shape:
        case SpellShapeEnum.X:
            return Cross(shape=shape, alternative_size=alternative_size, size=size)
        case SpellShapeEnum.L:
            return Line(alternative_size=0, size=size)
        case SpellShapeEnum.lower_l:
            return Line(
                alternative_size=alternative_size,
                size=size,
                stop_at_target=stop_at_target,
                caster_mp=caster_mp,
            )
        case SpellShapeEnum.T | SpellShapeEnum.D:
            return Cross(shape=shape, alternative_size=0, size=size)
        case SpellShapeEnum.C:
            return Lozenge(alternative_size=alternative_size, size=size)
        case SpellShapeEnum.O_CHAR:
            return Lozenge(alternative_size=size, size=size)
        case SpellShapeEnum.Q:
            return Cross(
                shape=shape,
                alternative_size=alternative_size if alternative_size else 1,
                size=size if size else 1,
            )
        case SpellShapeEnum.V:
            return Cone(alternative_size=0, size=size)
        case SpellShapeEnum.W:
            return Square(min_radius=0, size=size, is_diagonal_free=True)
        case SpellShapeEnum.plus:
            return Cross(
                shape=shape,
                alternative_size=0,
                size=size if size else 1,
                is_diagonal=True,
                is_all_directions=True,
            )
        case SpellShapeEnum.sharp:
            return Cross(
                shape=shape,
                alternative_size=alternative_size,
                size=size,
                is_diagonal=True,
                is_all_directions=True,
            )
        case SpellShapeEnum.slash:
            return Line(alternative_size=0, size=size)
        case SpellShapeEnum.star:
            return Cross(
                shape=shape,
                alternative_size=0,
                size=size,
                is_diagonal=False,
                is_all_directions=True,
            )
        case SpellShapeEnum.minus:
            return Cross(
                shape=shape,
                alternative_size=0,
                size=size,
                is_diagonal=True,
                is_all_directions=True,
            )
        case SpellShapeEnum.G:
            return Square(min_radius=0, size=size, is_diagonal_free=False)
        case SpellShapeEnum.I_CHAR:
            return Lozenge(alternative_size=size, size=63)
        case SpellShapeEnum.U:
            return HalfLozenge(alternative_size=0, size=size)
        case SpellShapeEnum.A | SpellShapeEnum.a:
            return Lozenge(alternative_size=0, size=63)
        case SpellShapeEnum.R:
            return Rectangle(alternative_size=alternative_size, size=size)
        case SpellShapeEnum.F:
            return Fork(size=size)

    return Cross(shape=shape, alternative_size=0, size=0)
