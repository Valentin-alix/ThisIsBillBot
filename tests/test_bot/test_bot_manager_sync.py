import threading
import unittest
from collections import defaultdict
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from src.core.bot.bot_manager import BotManager


def _account(login: str, account_id: int) -> dict[str, dict[str, int | str]]:
    return {"apikey": {"login": login, "accountId": account_id}}


def _bot(login: str, account_id: int) -> Any:
    bot = SimpleNamespace(
        account=_account(login, account_id),
        scheduler=SimpleNamespace(stop=MagicMock()),
        is_playing_event=SimpleNamespace(clear=MagicMock()),
        behavior_coordinator=SimpleNamespace(stop_behaviors=MagicMock()),
        connection_handler=SimpleNamespace(cleanup=MagicMock()),
        process_manager=SimpleNamespace(kill_process=MagicMock()),
        start=MagicMock(),
    )
    return bot


def _manager_with_bots(bots: dict[int, Any]) -> Any:
    manager = cast(Any, object.__new__(BotManager))
    manager.shared_signals = SimpleNamespace(
        bot_removed=SimpleNamespace(emit=MagicMock()),
        new_bot_added=SimpleNamespace(emit=MagicMock()),
    )
    manager.bot_by_account_id = bots
    manager._is_lauching_by_login = defaultdict(threading.Event)
    return manager


class BotManagerSynchronizeBotsTests(unittest.TestCase):
    def test_synchronize_removes_missing_bot_and_cleans_runtime(self) -> None:
        removed_bot = _bot("removed", 1)
        kept_bot = _bot("kept", 2)
        manager = _manager_with_bots({1: removed_bot, 2: kept_bot})
        manager._is_lauching_by_login["removed"].set()

        with patch(
            "src.core.bot.bot_manager.CryptoHelper.getStoredApiKeys",
            return_value=[_account("kept", 2)],
        ):
            manager.on_synchronize_bots()

        self.assertNotIn(1, manager.bot_by_account_id)
        self.assertIs(manager.bot_by_account_id[2], kept_bot)
        removed_bot.scheduler.stop.assert_called_once_with()
        removed_bot.is_playing_event.clear.assert_called_once_with()
        removed_bot.behavior_coordinator.stop_behaviors.assert_called_once_with()
        removed_bot.connection_handler.cleanup.assert_called_once_with()
        removed_bot.process_manager.kill_process.assert_called_once_with()
        self.assertNotIn("removed", manager._is_lauching_by_login)
        manager.shared_signals.bot_removed.emit.assert_called_once_with(removed_bot)

    def test_synchronize_adds_new_bot(self) -> None:
        manager = _manager_with_bots({})
        new_bot = _bot("new", 1)

        with (
            patch(
                "src.core.bot.bot_manager.CryptoHelper.getStoredApiKeys",
                return_value=[_account("new", 1)],
            ),
            patch(
                "src.core.bot.bot_manager.BotFactory.create_bot",
                return_value=new_bot,
            ) as create_bot,
        ):
            manager.on_synchronize_bots()

        self.assertIs(manager.bot_by_account_id[1], new_bot)
        create_bot = cast(MagicMock, create_bot)
        create_bot.assert_called_once_with(
            shared_signals=manager.shared_signals,
            account=_account("new", 1),
        )
        new_bot.start.assert_called_once_with()
        manager.shared_signals.new_bot_added.emit.assert_called_once_with(new_bot)

    def test_relaunch_ignores_missing_login(self) -> None:
        manager = _manager_with_bots({})

        result = manager.relaunch_account("missing")

        self.assertIsNone(result)
        self.assertNotIn("missing", manager._is_lauching_by_login)


if __name__ == "__main__":
    unittest.main()
