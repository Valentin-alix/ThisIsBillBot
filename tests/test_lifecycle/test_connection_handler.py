import logging
from threading import Event
from typing import cast
from unittest.mock import Mock

import pytest

from src.core.bot.lifecycle.connection_handler import ConnectionHandler
from src.core.events_manager.event_manager import (
    EventManager,
    ServerTextInformationError,
)
from src.services.logging_utils.loggers import BotLogger
from tests.fixtures.accounts import make_account


def test_rapid_disconnect_stop_logs_last_server_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    current_time = 1_000.0
    event_manager = EventManager(_logger=Mock())
    event_manager.last_text_information_error = ServerTextInformationError(
        message_id=89,
        parameters=("Zoween-Roxx",),
    )
    logger = logging.getLogger("test_connection_handler")
    caplog.set_level(logging.WARNING, logger=logger.name)
    is_playing_event = Event()
    is_playing_event.set()
    handler = ConnectionHandler(
        _logger=cast(BotLogger, logger),
        is_connected_event=Event(),
        is_ready_to_play_event=Event(),
        is_playing_event=is_playing_event,
        game_state=Mock(),
        dungeon_behavior=Mock(),
        fight_behavior=Mock(),
        character_creation_behavior=Mock(),
        tutorial_behavior=Mock(),
        account=make_account("test-login", 0),
        shared_signals=Mock(),
        get_bot_config=Mock(),
        event_manager=event_manager,
        behavior_coordinator=Mock(),
    )
    handler._last_disconnect_time = current_time
    handler._reconnect_attempts = 2
    monkeypatch.setattr(
        "src.core.bot.lifecycle.connection_handler.time.time",
        Mock(return_value=current_time + 1),
    )

    handler.on_disconnected()

    assert "id=89 params=['Zoween-Roxx']" in caplog.text
    assert not is_playing_event.is_set()
