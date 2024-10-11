import sys

from PyQt5.QtWidgets import QApplication

from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.core.logic.fight.spell import get_possible_mp_spell
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.zones.cone import Cone
from src.core.logic.zones.cross import Cross
from src.core.logic.zones.fork import Fork
from src.core.logic.zones.half_lozenge import HalfLozenge
from src.core.logic.zones.line import Line
from src.core.logic.zones.lozenge import Lozenge
from src.core.logic.zones.rectangle import Rectangle
from src.core.logic.zones.square import Square
from src.core.logic.zones.zone import Zone
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.gui.components.graphics.grid_widget import GridView
from src.interfaces.enums.spell_shape_enum import SpellShapeEnum
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import MapSignals


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
        case SpellShapeEnum.l:
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
        case SpellShapeEnum.O:
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
        case SpellShapeEnum.I:
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


if __name__ == "__main__":

    grid_signals = GridSignals()
    debug_signals = MapSignals()
    game_info_signals = GameInfoSignals()

    map_state = MapState(grid_signals=grid_signals)
    entity_state = EntityState(grid_signals=grid_signals)
    interactive_state = InteractiveState(grid_signals=grid_signals)
    player_state = PlayerState(
        game_info_signals=game_info_signals,
        interactive_state=interactive_state,
        entity_state=entity_state,
        map_state=map_state,
    )
    fight_state = FightState(
        game_info_signals=game_info_signals, player_state=player_state
    )
    player_state = PlayerState(
        map_state=map_state,
        game_info_signals=game_info_signals,
        entity_state=entity_state,
        interactive_state=interactive_state,
    )

    map_state.map_id = 154010373
    start = MapPoint.from_cell_id(270)
    end = MapPoint.from_cell_id(452)

    application = QApplication(sys.argv)
    widget = GridView(grid_signals=grid_signals, debug_signals=debug_signals)
    widget.on_new_map_id(map_state.map_id)

    spell_id = 12746

    spell = DataReader().spell_by_id[spell_id]
    print(I18N().name_by_id[spell.nameId])
    spell_level = DataReader().spell_lvl_by_spell_id[spell_id][0]
    print(spell_level)

    # direction = start.orientation_to(end)
    # for effect in spell_level.effects:
    #     zone_desc = effect.zoneDescr
    #     zone = get_zone_mps(
    #         shape=SpellShapeEnum(zone_desc.shape),
    #         alternative_size=zone_desc.param2,
    #         size=zone_desc.param1,
    #         caster_mp=start,
    #         stop_at_target=bool(zone_desc.isStopAtTarget),
    #     )
    #     for mp in zone.get_mps(mp=end, direction=direction):
    #         debug_signals.green_cell.emit(mp)
    #     break

    for mp in get_possible_mp_spell(
        MapPoint.from_cell_id(270), spell_level, 3, None, None, None
    ):
        debug_signals.green_cell.emit(mp)

    widget.show()

    application.exec()
