from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.models import RejectionStat
from src.core.engine.fights.los_detector import LosDetector
from src.core.engine.fights.spell import does_spell_need_test_los
from src.core.engine.fights.spell_modifier import SpellModifiers


def can_cast_spell_on_mp(
    context: AttackContext,
    from_mp: MapPoint,
    spell_lvl: SpellLevelsRootItem,
    mp: MapPoint,
    modifiers: SpellModifiers,
    entities_mp: set[MapPoint],
    entities_id_by_mp: dict[MapPoint, int],
    rejection_stats: dict[RejectionStat, int],
) -> bool:
    targetable_mp_data = MapReader().get_cell_data_by_cell_id(context.map_id, mp.cell_id)
    if not targetable_mp_data.mov or not targetable_mp_data.los:
        rejection_stats[RejectionStat.CELL_NOT_WALKABLE] += 1
        return False

    count_casted = context.count_casted_by_spell_id_on_current_turn.get(spell_lvl.spellId)
    entity_id = entities_id_by_mp.get(mp)
    if (
        count_casted is not None
        and entity_id is not None
        and modifiers.max_cast_per_target != 0
        and modifiers.max_cast_per_target <= count_casted
    ):
        rejection_stats[RejectionStat.MAX_CAST_PER_TARGET] += 1
        return False

    if does_spell_need_test_los(spell_lvl) and not LosDetector.los_between(
        map_id=context.map_id,
        taken_mps=entities_mp,
        start=from_mp,
        end=mp,
    ):
        rejection_stats[RejectionStat.NO_LOS] += 1
        return False

    return True
