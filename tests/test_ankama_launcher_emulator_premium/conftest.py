from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _isolate_resource_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.bot_storage.BOTS_STORAGE_PATH",
        tmp_path / "bots.local.json",
    )
    monkeypatch.setattr(
        "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.proxy.PROXIES_STORAGE_PATH",
        tmp_path / "proxies.json",
    )
    monkeypatch.setattr(
        "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.schedule_profile.SCHEDULE_PROFILES_PATH",
        tmp_path / "schedule_profiles.json",
    )
    monkeypatch.setattr(
        "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.mail_account.MAIL_ACCOUNTS_STORAGE_PATH",
        tmp_path / "mail_accounts.json",
    )
    monkeypatch.setattr(
        "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.debug_utils.DEBUG_DUMPS_DIR",
        tmp_path / "debug" / "dumps",
    )
