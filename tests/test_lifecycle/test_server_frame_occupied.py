from threading import Event

import pytest
from datas.protos.non_obf.game.basic_pb2 import TextInformationEvent
from datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent

from src.core.events_manager.event_manager import EventManager
from src.core.frames import server_frame as server_frame_module
from src.core.frames.server_frame import ServerFrame
from tests.fixtures.game_state import GameStateContext, make_game_state_ctx

OCCUPIED_ID = 999
_ERROR = TextInformationEvent.TextInformationType.TEXT_INFORMATION_ERROR


def _occupied_event(
    message_id: int = OCCUPIED_ID, parameters: list[str] | None = None
) -> TextInformationEvent:
    event = TextInformationEvent(message_type=_ERROR, message_id=message_id)
    event.parameters.extend(parameters or [])
    return event


def _build_frame(ctx: GameStateContext) -> tuple[EventManager, list[int]]:
    event_manager = EventManager(_logger=ctx.logger)
    ServerFrame(
        event_manager=event_manager,
        game_state=ctx.game_state,
        game_info_signals=ctx.game_info_signals,
        inventory_signals=ctx.inventory_signals,
        is_playing_event=Event(),
        _logger=ctx.logger,
    )

    disconnect_calls: list[int] = []
    event_manager.request_disconnect_callback = lambda: disconnect_calls.append(1)
    return event_manager, disconnect_calls


class TestOccupiedStuckCounter:
    def test_forces_disconnect_past_limit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # limit = 2 -> 3e occurrence consécutive déclenche
        monkeypatch.setattr(server_frame_module, "OCCUPIED_MESSAGE_ID", OCCUPIED_ID)
        monkeypatch.setattr(server_frame_module, "OCCUPIED_STUCK_LIMIT", 2)
        ctx = make_game_state_ctx()
        event_manager, disconnect_calls = _build_frame(ctx)

        event_manager.process_msg(_occupied_event())
        event_manager.process_msg(_occupied_event())
        assert disconnect_calls == []

        event_manager.process_msg(_occupied_event())
        assert disconnect_calls == [1]

    def test_map_change_resets_counter(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(server_frame_module, "OCCUPIED_MESSAGE_ID", OCCUPIED_ID)
        monkeypatch.setattr(server_frame_module, "OCCUPIED_STUCK_LIMIT", 2)
        ctx = make_game_state_ctx()
        event_manager, disconnect_calls = _build_frame(ctx)

        event_manager.process_msg(_occupied_event())
        event_manager.process_msg(_occupied_event())
        event_manager.process_msg(MapCurrentEvent(map_id=1))
        event_manager.process_msg(_occupied_event())
        event_manager.process_msg(_occupied_event())

        assert disconnect_calls == []

    def test_ignores_other_message_ids(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(server_frame_module, "OCCUPIED_MESSAGE_ID", OCCUPIED_ID)
        monkeypatch.setattr(server_frame_module, "OCCUPIED_STUCK_LIMIT", 2)
        ctx = make_game_state_ctx()
        event_manager, disconnect_calls = _build_frame(ctx)

        for _ in range(5):
            event_manager.process_msg(_occupied_event(message_id=OCCUPIED_ID + 1))

        assert disconnect_calls == []

    def test_records_last_text_error_for_disconnect_diagnostics(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(server_frame_module, "OCCUPIED_MESSAGE_ID", OCCUPIED_ID)
        ctx = make_game_state_ctx()
        event_manager, disconnect_calls = _build_frame(ctx)

        event_manager.process_msg(_occupied_event(message_id=89, parameters=["name"]))

        assert disconnect_calls == []
        assert event_manager.last_text_information_error is not None
        assert event_manager.last_text_information_error.message_id == 89
        assert event_manager.last_text_information_error.parameters == ("name",)

    def test_dormant_when_id_not_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(server_frame_module, "OCCUPIED_MESSAGE_ID", None)
        ctx = make_game_state_ctx()
        event_manager, disconnect_calls = _build_frame(ctx)

        for _ in range(5):
            event_manager.process_msg(_occupied_event())

        assert disconnect_calls == []
