import random
from collections.abc import Callable
from math import sqrt
from threading import Event
from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapCurrentEvent,
    MapMovementCancelRequest,
    MapMovementEvent,
    MapMovementRequest,
)
from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.behaviors.movements.map_movement_cancel_behavior import MapMovementCancelBehavior
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_element import PathElement
from src.core.events_manager.event_manager import EventManager
from src.core.events_manager.priority import PriorityEnum
from src.core.frames.entity_frame import EntityFrame
from tests.fixtures.game_state import GameStateContext


def test_map_movement_cancel_request_moves_player_to_cancel_cell(
    game_state_ctx: GameStateContext,
) -> None:
    game_state = game_state_ctx.game_state
    player_id = 42
    start_cell_id = 100
    cancel_cell_id = 250

    game_state.player.character_id = player_id
    game_state.entity.set_actor(
        ActorPositionInformation(
            actor_id=player_id,
            disposition=EntityDisposition(entity_id=player_id, cell_id=start_cell_id),
        )
    )

    event_manager = EventManager(_logger=game_state_ctx.logger)
    EntityFrame(
        event_manager=event_manager,
        game_state=game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        is_playing_event=Event(),
        _logger=game_state_ctx.logger,
    )

    event_manager.process_msg(MapMovementCancelRequest(cell_id=cancel_cell_id))

    assert game_state.entity.actor_by_id[player_id].disposition.cell_id == cancel_cell_id
    assert game_state.map.map_point.cell_id == cancel_cell_id


def test_map_change_stops_cancel_behavior_before_delayed_final_move(
    game_state_ctx: GameStateContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    game_state = game_state_ctx.game_state
    player_id = 42
    start_map_id = 193331715
    destination_map_id = 193331716
    start_map_point = MapPoint.from_cell_id(301)
    final_map_point = MapPoint.from_cell_id(135)
    final_move_path = MovementPath(
        start=start_map_point,
        end=final_map_point,
        path=[
            PathElement(step=start_map_point, orientation=DirectionsEnum.DOWN_LEFT),
            PathElement(step=MapPoint.from_cell_id(315), orientation=DirectionsEnum.UP_LEFT),
            PathElement(step=final_map_point, orientation=DirectionsEnum.DOWN_LEFT),
        ],
    )
    fake_map_point = MapPoint.from_cell_id(314)
    fake_move_path = MovementPath(
        start=start_map_point,
        end=fake_map_point,
        path=[
            PathElement(step=start_map_point, orientation=DirectionsEnum.DOWN_LEFT),
            PathElement(step=MapPoint.from_cell_id(315), orientation=DirectionsEnum.UP_LEFT),
            PathElement(step=fake_map_point, orientation=DirectionsEnum.DOWN_LEFT),
        ],
    )

    game_state.player.character_id = player_id
    game_state.map.map_id = start_map_id
    game_state.entity.set_actor(
        ActorPositionInformation(
            actor_id=player_id,
            disposition=EntityDisposition(entity_id=player_id, cell_id=start_map_point.cell_id),
        )
    )

    event_manager = EventManager(_logger=game_state_ctx.logger)
    monkeypatch.setattr(event_manager, "send", MagicMock())
    path_finding = MagicMock()
    path_finding.find_path.return_value = final_move_path
    map_move_behavior = MagicMock()
    behavior = MapMovementCancelBehavior(
        event_manager=event_manager,
        game_state=game_state,
        path_finding=path_finding,
        map_move_behavior=map_move_behavior,
        _logger=game_state_ctx.logger,
    )

    def return_fake_move_path(_final_move_path: MovementPath) -> MovementPath:
        return fake_move_path

    monkeypatch.setattr(behavior, "_find_fake_move_path", return_fake_move_path)
    scheduled_callbacks: list[Callable[[], None]] = []

    def capture_timer(
        _delay: tuple[float, float] | float,
        callback_to_schedule: Callable[[], None],
    ) -> None:
        scheduled_callbacks.append(callback_to_schedule)

    monkeypatch.setattr(behavior, "run_timer", capture_timer)
    callback = MagicMock()

    behavior.start(
        final_move_path=final_move_path,
        cancellation_probability=1,
        callback=callback,
        parent=None,
    )
    event_manager.process_msg(
        MapMovementEvent(
            character_id=player_id,
            cells=[start_map_point.cell_id, 315, fake_map_point.cell_id],
        )
    )
    scheduled_callbacks.pop(0)()
    delayed_final_move = scheduled_callbacks.pop(0)

    def fire_timer_during_frame_update(_message: MapCurrentEvent) -> None:
        behavior.run_timed_func(delayed_final_move)

    event_manager.on(
        MapCurrentEvent,
        fire_timer_during_frame_update,
        originator=MagicMock(),
        priority=PriorityEnum.FRAME,
    )
    event_manager.process_msg(MapCurrentEvent(map_id=destination_map_id))

    callback.assert_called_once_with(MapMoveError.UNEXPECTED_NEW_MAP)
    map_move_behavior.start.assert_not_called()


def test_cancel_behavior_stops_one_to_three_cells_before_destination(
    game_state_ctx: GameStateContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    game_state = game_state_ctx.game_state
    start_map_point = MapPoint.from_cell_id(301)
    final_map_point = MapPoint.from_cell_id(135)
    final_move_path = MovementPath(
        start=start_map_point,
        end=final_map_point,
        path=[
            PathElement(step=start_map_point, orientation=DirectionsEnum.DOWN_LEFT),
            PathElement(step=MapPoint.from_cell_id(315), orientation=DirectionsEnum.UP_LEFT),
            PathElement(step=MapPoint.from_cell_id(314), orientation=DirectionsEnum.DOWN_LEFT),
            PathElement(step=final_map_point, orientation=DirectionsEnum.UP_LEFT),
        ],
    )
    fake_map_point = MapPoint.from_cell_id(312)
    fake_move_path = MovementPath(
        start=start_map_point,
        end=fake_map_point,
        path=[
            PathElement(step=start_map_point, orientation=DirectionsEnum.DOWN_LEFT),
            PathElement(step=MapPoint.from_cell_id(315), orientation=DirectionsEnum.UP_LEFT),
            PathElement(step=MapPoint.from_cell_id(314), orientation=DirectionsEnum.DOWN_LEFT),
            PathElement(step=MapPoint.from_cell_id(313), orientation=DirectionsEnum.UP_LEFT),
            PathElement(step=fake_map_point, orientation=DirectionsEnum.DOWN_LEFT),
        ],
    )
    game_state.player.character_id = 42
    game_state.map.map_id = 193331715
    game_state.entity.set_actor(
        ActorPositionInformation(
            actor_id=42,
            disposition=EntityDisposition(entity_id=42, cell_id=start_map_point.cell_id),
        )
    )
    event_manager = EventManager(_logger=game_state_ctx.logger)
    event_manager_send = MagicMock()
    monkeypatch.setattr(event_manager, "send", event_manager_send)
    path_finding = MagicMock()
    map_move_behavior = MagicMock()
    behavior = MapMovementCancelBehavior(
        event_manager=event_manager,
        game_state=game_state,
        path_finding=path_finding,
        map_move_behavior=map_move_behavior,
        _logger=game_state_ctx.logger,
    )
    scheduled_callbacks: list[Callable[[], None]] = []

    def capture_timer(
        _delay: tuple[float, float] | float,
        callback_to_schedule: Callable[[], None],
    ) -> None:
        scheduled_callbacks.append(callback_to_schedule)

    def select_two_remaining_cells(_minimum: int, _maximum: int) -> int:
        return 2

    def return_fake_move_path(_final_move_path: MovementPath) -> MovementPath:
        return fake_move_path

    monkeypatch.setattr(behavior, "run_timer", capture_timer)
    monkeypatch.setattr(behavior, "_find_fake_move_path", return_fake_move_path)
    monkeypatch.setattr(
        "src.core.behaviors.movements.map_movement_cancel_behavior.random.randint",
        select_two_remaining_cells,
    )

    behavior.start(
        final_move_path=final_move_path,
        cancellation_probability=1,
        callback=MagicMock(),
        parent=None,
    )
    event_manager.process_msg(
        MapMovementEvent(
            character_id=42,
            cells=[start_map_point.cell_id, 315, 314, 313, fake_map_point.cell_id],
        )
    )
    scheduled_callbacks.pop(0)()

    event_manager_send.assert_any_call(MapMovementCancelRequest(cell_id=314))
    event_manager_send.assert_any_call(
        MapMovementRequest(
            key_cells=fake_move_path.get_key_cells(),
            map_id=game_state.map.map_id,
        )
    )


def test_cancel_behavior_moves_to_a_lateral_destination_before_the_final_destination(
    game_state_ctx: GameStateContext,
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    random.seed(0)
    game_state = game_state_ctx.game_state
    start_map_point = MapPoint.from_cell_id(301)
    final_map_point = MapPoint.from_cell_id(135)
    final_move_path = MovementPath(
        start=start_map_point,
        end=final_map_point,
        path=[
            PathElement(step=start_map_point, orientation=DirectionsEnum.DOWN_LEFT),
            PathElement(step=MapPoint.from_cell_id(315), orientation=DirectionsEnum.UP_LEFT),
            PathElement(step=final_map_point, orientation=DirectionsEnum.DOWN_LEFT),
        ],
    )
    game_state.player.character_id = 42
    game_state.map.map_id = 193331715
    game_state.entity.set_actor(
        ActorPositionInformation(
            actor_id=42,
            disposition=EntityDisposition(entity_id=42, cell_id=start_map_point.cell_id),
        )
    )
    event_manager = EventManager(_logger=game_state_ctx.logger)
    monkeypatch.setattr(event_manager, "send", MagicMock())
    selected_destinations: list[MapPoint] = []

    def return_path_to_candidate(
        _context: object,
        path_start: MapPoint,
        candidates: set[MapPoint],
    ) -> MovementPath:
        candidate = next(iter(candidates))
        selected_destinations.append(candidate)
        return MovementPath(
            start=path_start,
            end=candidate,
            path=[
                PathElement(step=path_start, orientation=path_start.orientation_to(candidate)),
                PathElement(step=MapPoint.from_cell_id(315), orientation=DirectionsEnum.UP_LEFT),
            ],
        )

    path_finding = MagicMock()
    path_finding.find_path.side_effect = return_path_to_candidate
    behavior = MapMovementCancelBehavior(
        event_manager=event_manager,
        game_state=game_state,
        path_finding=path_finding,
        map_move_behavior=MagicMock(),
        _logger=game_state_ctx.logger,
    )

    behavior.start(
        final_move_path=final_move_path,
        cancellation_probability=1,
        callback=MagicMock(),
        parent=None,
    )

    assert len(selected_destinations) == 1
    fake_destination = selected_destinations[0]
    path_delta_x = final_map_point.x - start_map_point.x
    path_delta_y = final_map_point.y - start_map_point.y
    fake_delta_x = fake_destination.x - start_map_point.x
    fake_delta_y = fake_destination.y - start_map_point.y
    projection = fake_delta_x * path_delta_x + fake_delta_y * path_delta_y
    lateral_distance = abs(fake_delta_x * path_delta_y - fake_delta_y * path_delta_x) / sqrt(
        path_delta_x**2 + path_delta_y**2
    )

    assert 0 < projection < path_delta_x**2 + path_delta_y**2
    assert 2.5 <= lateral_distance <= 5.5
