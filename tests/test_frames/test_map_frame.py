from threading import Event

from datas.protos.non_obf.game.anomaly_pb2 import AnomalySubareaInformationRequest
from datas.protos.non_obf.game.context_pb2 import ContextCreationEvent, ContextReadyRequest
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapCurrentEvent,
    MapInformationRequest,
)
from google.protobuf.message import Message

from src.core.events_manager.event_manager import EventManager
from src.core.frames.map_frame import MapFrame
from tests.fixtures.game_state import GameStateContext


def _make_map_frame(
    game_state_ctx: GameStateContext,
    sent_messages: list[Message],
) -> tuple[EventManager, MapFrame]:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    event_manager.is_socket_mode = True
    event_manager.on_send_game_callback = sent_messages.append
    map_frame = MapFrame(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        is_playing_event=Event(),
        world_signals=game_state_ctx.world_signals,
        _logger=game_state_ctx.logger,
    )
    return event_manager, map_frame


def test_socket_roleplay_context_requests_map_information(
    game_state_ctx: GameStateContext,
) -> None:
    sent_messages: list[Message] = []
    event_manager, _map_frame = _make_map_frame(game_state_ctx, sent_messages)

    event_manager.process_msg(
        ContextCreationEvent(context=ContextCreationEvent.ROLE_PLAY)
    )
    event_manager.process_msg(MapCurrentEvent(map_id=12345))

    assert [message.__class__ for message in sent_messages] == [
        AnomalySubareaInformationRequest,
        ContextReadyRequest,
        MapInformationRequest,
    ]


def test_socket_fight_context_skips_map_information_request(
    game_state_ctx: GameStateContext,
) -> None:
    sent_messages: list[Message] = []
    event_manager, _map_frame = _make_map_frame(game_state_ctx, sent_messages)

    event_manager.process_msg(ContextCreationEvent(context=ContextCreationEvent.FIGHT))
    event_manager.process_msg(MapCurrentEvent(map_id=12345))

    assert not any(isinstance(message, MapInformationRequest) for message in sent_messages)
    assert [message.__class__ for message in sent_messages] == [
        AnomalySubareaInformationRequest,
        ContextReadyRequest,
    ]


def test_socket_context_switch_back_to_roleplay_requests_map_information(
    game_state_ctx: GameStateContext,
) -> None:
    sent_messages: list[Message] = []
    event_manager, _map_frame = _make_map_frame(game_state_ctx, sent_messages)

    event_manager.process_msg(ContextCreationEvent(context=ContextCreationEvent.FIGHT))
    event_manager.process_msg(MapCurrentEvent(map_id=12345))
    sent_messages.clear()
    event_manager.process_msg(
        ContextCreationEvent(context=ContextCreationEvent.ROLE_PLAY)
    )
    event_manager.process_msg(MapCurrentEvent(map_id=67890))

    assert [message.__class__ for message in sent_messages] == [
        ContextReadyRequest,
        MapInformationRequest,
    ]
