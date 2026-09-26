from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest

from ankama_launcher_emulator.controller.bot_storage import BotStorageController
from ankama_launcher_emulator.controller.mail_account import MailAccountController
from ankama_launcher_emulator.interfaces.local_storage import BotRecord
from ankama_launcher_emulator.interfaces.mail_account import ManualAccountConfig
from src.core.bot.bot import Bot
from src.core.bot.bot_manager import BotManager


def test_account_deletion_stops_bot_and_preserves_mailbox_until_deleted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "ankama_launcher_emulator.controller.bot_storage.BOTS_STORAGE_PATH", tmp_path / "bots.json"
    )
    monkeypatch.setattr(
        "ankama_launcher_emulator.controller.mail_account.MAIL_ACCOUNTS_STORAGE_PATH", tmp_path / "mail.json"
    )
    storage = BotStorageController()
    storage.upsert_record(
        "account", lambda: BotRecord(email="account@example.com", hardware_id="hw"), lambda _: None
    )
    mailboxes = MailAccountController()
    mailboxes.save_config("account@example.com", ManualAccountConfig(), create=True)

    manager = BotManager.__new__(BotManager)
    bot = Mock()
    bot.account.apikey.login = "account"
    manager.bot_by_account_id = {1: cast(Bot, bot)}
    synchronized = Mock()
    monkeypatch.setattr(manager, "on_synchronize_bots", synchronized)
    remove_key = Mock()
    remove_snapshot = Mock()
    monkeypatch.setattr("src.core.bot.bot_manager.CryptoHelper.remove_bot", remove_key)
    monkeypatch.setattr("src.core.bot.bot_manager.PlayerInfoStorage.remove_snapshot", remove_snapshot)

    manager.delete_account("account")

    assert storage.get_record("account") is None
    bot.bot_signals.stop.emit.assert_called_once_with()
    remove_key.assert_called_once_with("account")
    remove_snapshot.assert_called_once_with("account")
    synchronized.assert_called_once_with()
    assert mailboxes.get_config("account@example.com") is not None

    manager.delete_mailbox("account@example.com")

    assert mailboxes.get_all_entries() == {}
