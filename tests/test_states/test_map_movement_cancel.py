from threading import Event

from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)
from datas.protos.non_obf.game.gamemap_pb2 import MapMovementCancelRequest

from src.core.events_manager.event_manager import EventManager
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
