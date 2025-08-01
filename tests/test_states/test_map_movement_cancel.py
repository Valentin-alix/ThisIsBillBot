from collections.abc import Callable
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
    decoy_map_point = MapPoint.from_cell_id(311)
    final_map_point = MapPoint.from_cell_id(135)
    decoy_path = MovementPath(
        start=start_map_point,
        end=decoy_map_point,
        path=[
            PathElement(step=start_map_point, orientation=DirectionsEnum.DOWN_RIGHT),
            PathElement(step=MapPoint.from_cell_id(315), orientation=DirectionsEnum.UP_LEFT),
        ],
    )
    final_move_path = MovementPath(
        start=start_map_point,
        end=final_map_point,
        path=[PathElement(step=start_map_point, orientation=DirectionsEnum.DOWN_LEFT)],
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
    path_finding.find_path.return_value = decoy_path
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

    monkeypatch.setattr(behavior, "run_timer", capture_timer)
    callback = MagicMock()

    behavior.start(final_move_path=final_move_path, callback=callback, parent=None)
    event_manager.process_msg(
        MapMovementEvent(
            character_id=player_id,
            cells=[start_map_point.cell_id, 315, decoy_map_point.cell_id],
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
