from collections.abc import Iterable
from dataclasses import dataclass, field

from dofus_unity_reader.data_center.map_reader import MapReader
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.contexts import FightReachableContext
from src.core.engine.fights.reachable_cells.reachable_mp_node import (
    ReachableMpNode,
)
from src.core.signals.world_signals import MapSignals


@dataclass
class FightReachableCells:
    debug_signals: MapSignals | None = None

    reachable_cost_by_mp: dict[MapPoint, int] = field(init=False, default_factory=dict[MapPoint, int])
    node_by_mp: dict[MapPoint, ReachableMpNode] = field(
        init=False, default_factory=dict[MapPoint, ReachableMpNode]
    )
    open_node: set[ReachableMpNode] = field(init=False, default_factory=set[ReachableMpNode])

    def search(
        self,
        context: FightReachableContext,
        enemies_mp: set[MapPoint],
        entities_mp: Iterable[MapPoint],
    ) -> dict[MapPoint, int]:
        self.open_node.clear()
        self.node_by_mp.clear()
        self.reachable_cost_by_mp.clear()

        self.open_node.add(
            ReachableMpNode(
                mp=context.player_map_point,
                best_remaining_pm_no_tackle=context.movement_points,
            )
        )

        while self.open_node:
            node: ReachableMpNode = self.open_node.pop()
            remaining_pm_no_tackle = node.best_remaining_pm_no_tackle - 1
            if remaining_pm_no_tackle < 0 or enemies_mp & node.mp.side_map_points:
                continue
            for side_mp in node.mp.side_map_points:
                self.mark_node(context, side_mp, remaining_pm_no_tackle, entities_mp)

        if self.debug_signals:
            for mp in self.reachable_cost_by_mp:
                self.debug_signals.green_cell.emit(mp)

        return self.reachable_cost_by_mp

    def mark_node(
        self,
        context: FightReachableContext,
        mp: MapPoint,
        remaining_not_tackled_pm: int,
        entities_mp: Iterable[MapPoint],
    ) -> None:
        node = self.node_by_mp.get(mp)
        if node is None:
            cell_data = MapReader().get_cell_data_by_cell_id(context.map_id, mp.cell_id)
            if mp in entities_mp or not cell_data.mov or cell_data.nonWalkableDuringFight:
                return

            node = ReachableMpNode(mp=mp, best_remaining_pm_no_tackle=remaining_not_tackled_pm)
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
