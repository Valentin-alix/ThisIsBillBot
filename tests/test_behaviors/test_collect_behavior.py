from collections.abc import Callable
from typing import cast

from dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.interactives.collect_behavior import CollectBehavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.engine.interactives.collectable import Collectable
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.events_manager.event_manager import EventManager
from src.core.states.game_state import GameState
from tests.fixtures.game_state import GameStateContext, set_game_state
from tests.fixtures.interactives import make_collectable

PLAYER_ID = -1


def _make_move_path(start_cell_id: int, end_cell_id: int) -> MovementPath:
    path_elements = MovementPath.get_path_elements_from_cells(
        [start_cell_id, end_cell_id]
    )
    return MovementPath(
        start=MapPoint.from_cell_id(start_cell_id),
        end=MapPoint.from_cell_id(end_cell_id),
        path=path_elements,
    )


class ImmediateMapMoveBehavior:
    def __init__(self, game_state: GameState) -> None:
        self._game_state = game_state

    def start(
        self,
        callback: Callable[[str | None], None],
        parent: object,
        move_path: MovementPath,
    ) -> None:
        del parent
        actor = self._game_state.entity.actor_by_id[PLAYER_ID]
        self._game_state.entity.update_actor_disposition(
            actor_id=PLAYER_ID,
            direction=actor.disposition.direction,
            cell_id=move_path.end.cell_id,
        )
        callback(None)


class InteractiveBehaviorFake:
    def __init__(self, map_move_behavior: ImmediateMapMoveBehavior) -> None:
        self.map_move_behavior = map_move_behavior
        self.collected_move_paths: list[MovementPath] = []

    def start(
        self,
        callback: Callable[[str | None], None],
        parent: object,
        move_path: MovementPath,
        element_id: int,
        skill_instance_uid: int,
    ) -> None:
        del callback, parent, element_id, skill_instance_uid
        self.collected_move_paths.append(move_path)


class PathFindingFake:
    def __init__(self, look_path: MovementPath) -> None:
        self._look_path = look_path

    def find_path(
        self,
        context: object,
        start: MapPoint,
        ends: set[MapPoint],
    ) -> MovementPath:
        del context, start, ends
        return self._look_path


def test_collect_after_look_around_recalculates_path_from_current_cell(
    game_state_ctx: GameStateContext,
) -> None:
    initial_cell_id = 315
    look_around_cell_id = 479
    collect_cell_id = 368
    set_game_state(
        game_state_ctx.game_state,
        player_cell_id=initial_cell_id,
        enemy_cell_ids=[],
    )
    collectable = make_collectable(element_id=10)
    look_path = _make_move_path(initial_cell_id, look_around_cell_id)
    interactive_behavior = InteractiveBehaviorFake(
        ImmediateMapMoveBehavior(game_state_ctx.game_state)
    )
    collect_behavior = CollectBehavior(
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state_ctx.game_state,
        interactive_behavior=cast(InteractiveBehavior, interactive_behavior),
        path_finding=cast(Pathfinding, PathFindingFake(look_path)),
        _logger=game_state_ctx.logger,
    )
    recalculated_starts: list[MapPoint] = []

    def get_near_collectable_from_current_cell(
        collectables: list[Collectable],
    ) -> tuple[MovementPath, Collectable] | None:
        current_map_point = game_state_ctx.game_state.map.map_point
        recalculated_starts.append(current_map_point)
        fresh_move_path = _make_move_path(current_map_point.cell_id, collect_cell_id)
        return fresh_move_path, collectables[0]

    def run_timer_immediately(
        range_time: tuple[float, float] | float,
        func: Callable[[], None],
    ) -> None:
        del range_time
        func()

    collect_behavior.get_near_collectable = get_near_collectable_from_current_cell
    collect_behavior.run_timer = run_timer_immediately
    collect_behavior._get_random_walkable_cell_nearby = lambda: MapPoint.from_cell_id(
        look_around_cell_id
    )

    collect_behavior._do_look_around(
        _make_move_path(initial_cell_id, collect_cell_id), collectable
    )

    assert recalculated_starts == [MapPoint.from_cell_id(look_around_cell_id)]
    assert interactive_behavior.collected_move_paths == [
        _make_move_path(look_around_cell_id, collect_cell_id)
    ]
