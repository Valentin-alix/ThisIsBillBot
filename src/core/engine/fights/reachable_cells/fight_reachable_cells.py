from dataclasses import dataclass, field
from typing import Iterable

from D3Database.data_center.map_reader import MapReader
from D3Database.enums.characteristic_enum import CharacteristicEnum
from D3Database.grid.map_point import MapPoint
from src.core.engine.fights.reachable_cells.reachable_mp_node import (
    ReachableMpNode,
)
from src.core.signals.world_signals import MapSignals
from src.core.states.game_state import GameState


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
        self, enemies_mp: set[MapPoint], entities_mp: Iterable[MapPoint]
    ) -> dict[MapPoint, int]:
        self.open_node.clear()
        self.node_by_mp.clear()
        self.reachable_cost_by_mp.clear()

        self.open_node.add(
            ReachableMpNode(
                mp=self.game_state.map.map_point,
                best_remaining_pm_no_tackle=self.game_state.fight.get_stat_by_id(
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
        self,
        mp: MapPoint,
        remaining_not_tackled_pm: int,
        entities_mp: Iterable[MapPoint],
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
