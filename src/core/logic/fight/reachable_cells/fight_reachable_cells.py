import sys
from dataclasses import dataclass, field

from PyQt5.QtWidgets import QApplication

from src.core.data_center.map_reader import MapReader
from src.core.logic.fight.reachable_cells.reachable_mp_node import (
    ReachableMpNode,
)
from src.core.logic.grid.map_point import MapPoint
from src.core.states.game_state import GameState
from src.gui.components.graphics.grid_widget import GridView
from src.interfaces.enums.characteristic_enum import CharacteristicEnum
from src.signals.grid_signals import GridSignals
from src.signals.world_signals import MapSignals


@dataclass
class FightReachableCells:
    game_state: GameState
    debug_signals: MapSignals | None = None

    reachable_cost_by_mp: dict[MapPoint, int] = field(init=False, default_factory=dict)
    node_by_mp: dict[MapPoint, ReachableMpNode] = field(
        init=False, default_factory=dict
    )
    open_node: set[ReachableMpNode] = field(init=False, default_factory=set)

    def search(
        self, enemies_mp: set[MapPoint], entities_mp: set[MapPoint]
    ) -> dict[MapPoint, int]:
        self.open_node.clear()
        self.node_by_mp.clear()
        self.reachable_cost_by_mp.clear()

        self.open_node.add(
            ReachableMpNode(
                mp=self.game_state.player.map_point,
                best_remaining_pm_no_tackle=self.game_state.player.get_stat_by_id(
                    CharacteristicEnum.MOVEMENT_POINTS
                ),
            )
        )

        while self.open_node:
            node = self.open_node.pop()
            remaining_pm_no_tackle = node.best_remaining_pm_no_tackle - 1
            if remaining_pm_no_tackle < 0 or enemies_mp & node.mp.side_map_points:
                continue
            for side_mp in node.mp.side_map_points:
                self.mark_node(side_mp, remaining_pm_no_tackle, entities_mp)

        if self.debug_signals:
            for mp in self.reachable_cost_by_mp:
                self.debug_signals.green_cell.emit(mp)

        return self.reachable_cost_by_mp

    def mark_node(
        self, mp: MapPoint, remaining_not_tackled_pm: int, entities_mp: set[MapPoint]
    ) -> None:
        node = self.node_by_mp.get(mp)
        if node is None:
            cell_data = MapReader().get_cell_data_by_cell_id(
                self.game_state.map.map_id, mp.cell_id
            )
            if (
                mp in entities_mp
                or not cell_data.mov
                or cell_data.nonWalkableDuringFight
            ):
                return

            node = ReachableMpNode(
                mp=mp, best_remaining_pm_no_tackle=remaining_not_tackled_pm
            )
            self.open_node.add(node)
            self.node_by_mp[mp] = node
            self.reachable_cost_by_mp[mp] = remaining_not_tackled_pm
        else:
            if not remaining_not_tackled_pm > node.best_remaining_pm_no_tackle:
                return
            node.best_remaining_pm_no_tackle = remaining_not_tackled_pm
            self.reachable_cost_by_mp[mp] = remaining_not_tackled_pm
            if node not in self.open_node:
                self.open_node.add(node)


if __name__ == "__main__":
    grid_signals = GridSignals()
    debug_signals = MapSignals()

    map_id = 153880321
    player_mp = MapPoint.from_cell_id(497)
    enemies_mp = {
        MapPoint.from_cell_id(457),
        MapPoint.from_cell_id(442),
        MapPoint.from_cell_id(469),
    }

    application = QApplication(sys.argv)
    widget = GridView(grid_signals=grid_signals, debug_signals=debug_signals)
    widget.on_new_map_id(map_id)

    debug_signals.white_cell.emit(player_mp)
    debug_signals.red_cells.emit(enemies_mp)

    fight_reachable_cells = FightReachableCells(
        map_id=map_id,
        from_mp=player_mp,
        pm=3,
        debug_signals=debug_signals,
        enemies_mp=enemies_mp,
        entities_mp=enemies_mp | {player_mp},
    )
    fight_reachable_cells.search()

    widget.show()

    application.exec()
