from collections.abc import Callable

from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.reachable_cells.fight_reachable_cells import FightReachableCells

SupportAction = tuple[MapPoint, SpellLevelsRootItem, MapPoint]
SupportActionRule = Callable[[AttackContext, FightReachableCells, DamageCalculator], SupportAction | None]
ReservedApProvider = Callable[[AttackContext, DamageCalculator], int]
