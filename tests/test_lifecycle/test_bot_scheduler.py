from typing import cast
from unittest.mock import Mock

import pytest

from src.core.bot.lifecycle.scheduler import BotScheduler


class TestBotSchedulerPlannedStop:
    def test_socket_stop_closes_active_socket_connection(
        self, bot_scheduler: BotScheduler
    ) -> None:
        bot_scheduler.is_playing_event.set()
        bot_scheduler.event_manager.is_socket_mode = True
        request_disconnect = Mock()
        bot_scheduler.event_manager.request_disconnect_callback = request_disconnect

        bot_scheduler._planned_stop_bot()

        request_disconnect.assert_called_once()
        cast(Mock, bot_scheduler.process_manager.kill_process).assert_called_once()

    def test_non_socket_stop_keeps_existing_process_only_disconnect_behavior(
        self, bot_scheduler: BotScheduler
    ) -> None:
        bot_scheduler.is_playing_event.set()
        request_disconnect = Mock()
        bot_scheduler.event_manager.request_disconnect_callback = request_disconnect

        bot_scheduler._planned_stop_bot()

        request_disconnect.assert_not_called()
        cast(Mock, bot_scheduler.process_manager.kill_process).assert_called_once()

    def test_socket_stop_requires_disconnect_callback(
        self, bot_scheduler: BotScheduler
    ) -> None:
        bot_scheduler.is_playing_event.set()
        bot_scheduler.event_manager.is_socket_mode = True

        with pytest.raises(AssertionError, match="request_disconnect_callback"):
            bot_scheduler._planned_stop_bot()
