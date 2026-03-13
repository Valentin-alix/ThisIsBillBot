from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_resource_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("ankama_launcher_emulator.controller.bot_storage.BOTS_STORAGE_PATH", tmp_path / "bots.json")
    monkeypatch.setattr("ankama_launcher_emulator.controller.proxy.PROXIES_STORAGE_PATH", tmp_path / "proxies.json")
    monkeypatch.setattr("ankama_launcher_emulator.controller.schedule_profile.SCHEDULE_PROFILES_PATH", tmp_path / "schedule_profiles.json")
    monkeypatch.setattr("ankama_launcher_emulator.controller.mail_account.MAIL_ACCOUNTS_STORAGE_PATH", tmp_path / "mail_accounts.json")
