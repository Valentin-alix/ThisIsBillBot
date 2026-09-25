from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from threading import Barrier, BrokenBarrierError
from unittest.mock import Mock

import pytest
import schedule

from ankama_launcher_emulator.controller.mail_account import MailAccountController
from ankama_launcher_emulator.controller.proxy import ProxyController
from ankama_launcher_emulator.controller.schedule_profile import ScheduleProfileController
from ankama_launcher_emulator.controller.paysafecard_pool import PaysafecardPoolController
from ankama_launcher_emulator.interfaces.mail_account import ManualAccountConfig, SmailProAccountConfig
from ankama_launcher_emulator.interfaces.schedule_profile import ProxyConfig, ScheduleProfile, TimeSlot
from src.controller import settings as settings_module
from src.controller.settings import SettingsService
from src.core.config import BehaviorSettings, GlobalSettings
from src.core.bot.bot import Bot
from src.core.bot.lifecycle.scheduler import BotScheduler
from src.utils.runtime_support import RuntimeSetupError


@pytest.fixture(autouse=True)
def isolated_storage(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "ankama_launcher_emulator.controller.mail_account.MAIL_ACCOUNTS_STORAGE_PATH", tmp_path / "mail.json"
    )
    monkeypatch.setattr(
        "ankama_launcher_emulator.controller.proxy.PROXIES_STORAGE_PATH", tmp_path / "proxies.json"
    )
    monkeypatch.setattr(
        "ankama_launcher_emulator.controller.schedule_profile.SCHEDULE_PROFILES_PATH",
        tmp_path / "profiles.json",
    )


def test_settings_roundtrip_and_failed_write_preserve_previous_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SettingsService()
    assert service.get() == GlobalSettings()
    service.update_behaviors(BehaviorSettings(do_craft=True, do_fighter=False), True)
    service.update_sonji_key("local-key")
    persisted = GlobalSettings.model_validate_json(settings_module.SETTINGS_PATH.read_text())
    assert persisted.behaviors.do_craft
    assert not persisted.behaviors.do_fighter
    assert persisted.enable_account_automation
    assert persisted.sonji_api_key == "local-key"
    monkeypatch.setattr(service, "_settings", None)
    assert service.get() == persisted

    def fail(*_args: object, **_kwargs: object) -> None:
        raise OSError("test")

    monkeypatch.setattr(settings_module, "atomic_write_text", fail)
    with pytest.raises(OSError):
        service.update_sonji_key("replacement")
    assert service.get() == persisted
    assert GlobalSettings.model_validate_json(settings_module.SETTINGS_PATH.read_text()) == persisted


def test_invalid_settings_are_reported_without_resetting_file() -> None:
    settings_module.SETTINGS_PATH.write_text('{"behaviors":{"do_craft":"invalid"}}')
    with pytest.raises(RuntimeSetupError):
        SettingsService().get()
    assert "invalid" in settings_module.SETTINGS_PATH.read_text()


def test_legacy_quest_setting_is_removed_and_other_settings_are_preserved() -> None:
    settings_module.SETTINGS_PATH.write_text(
        '{"behaviors":{"do_quest":true,"do_craft":true},"sonji_api_key":"keep"}',
        encoding="utf-8",
    )

    settings = SettingsService().get()

    assert settings.behaviors.do_craft
    assert settings.sonji_api_key == "keep"
    persisted = settings_module.SETTINGS_PATH.read_text(encoding="utf-8")
    assert "do_quest" not in persisted
    assert GlobalSettings.model_validate_json(persisted) == settings


def test_service_key_precedence_and_concurrent_updates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SONJI_API_KEY", "environment-key")
    service = SettingsService()
    assert service.sonji_api_key() == "environment-key"
    with ThreadPoolExecutor(max_workers=2) as pool:
        key_write = pool.submit(service.update_sonji_key, "gui-key")
        behavior_write = pool.submit(service.update_behaviors, BehaviorSettings(do_craft=True), True)
        key_write.result()
        behavior_write.result()
    assert service.sonji_api_key() == "gui-key"
    assert service.get().behaviors.do_craft
    service.update_sonji_key("")
    assert service.sonji_api_key() is None
    service.update_sonji_key(None)
    assert service.sonji_api_key() == "environment-key"


def test_running_bot_keeps_settings_until_next_manual_or_planned_start(runtime_bot: Bot) -> None:
    bot = runtime_bot
    service = SettingsService()
    original = bot.game_state.settings
    changed = BehaviorSettings(do_craft=True, do_fighter=False, do_use_guild_chest=True, do_sale_hotel=False)
    service.update_behaviors(changed, False)
    assert bot.game_state.settings == original
    bot.behavior_coordinator.on_play(True)
    assert bot.game_state.settings == changed
    assert bot.game_state.guild_chest.settings == changed
    next_settings = BehaviorSettings(do_dungeon=True)
    service.update_behaviors(next_settings, False)
    assert bot.game_state.settings == changed
    start = datetime.now()
    bot.auto_bot_behavior.start_planned_session(start, start + timedelta(hours=2))
    assert bot.game_state.settings == next_settings
    bot.is_playing_event.clear()


def test_schedule_edit_waits_for_active_session_to_stop(
    bot_scheduler: BotScheduler, monkeypatch: pytest.MonkeyPatch
) -> None:
    rebuild = Mock()
    monkeypatch.setattr(bot_scheduler, "refresh_configuration", rebuild)
    bot_scheduler.is_playing_event.set()
    bot_scheduler.request_configuration_refresh()
    rebuild.assert_not_called()
    bot_scheduler.is_playing_event.clear()
    bot_scheduler.apply_pending_configuration()
    rebuild.assert_called_once()
    bot_scheduler.apply_pending_configuration()
    rebuild.assert_called_once()


def test_mail_edits_preserve_usage_quarantine_and_consumed_messages() -> None:
    controller = MailAccountController()
    email = "test@example.com"
    config = SmailProAccountConfig(api_key="key", email=email, timestamp=123)
    controller.save_config(email, config, create=True)
    controller.mark_used(email)
    controller.quarantine(email, "test reason")
    controller.record_smailpro_message_consumed(email, "message-1")
    controller.save_config(email, config.model_copy(update={"api_key": "new-key"}))
    entry = controller.get_all_entries()[email]
    assert entry.is_used and entry.bad_state
    assert entry.quarantine_reason == "test reason"
    assert isinstance(entry.config, SmailProAccountConfig)
    assert entry.config.consumed_message_ids == ["message-1"]
    with pytest.raises(ValueError):
        controller.save_config(email, ManualAccountConfig(), create=True)


def test_proxy_edits_preserve_rejection_and_runtime_quotas() -> None:
    controller = ProxyController()
    config = ProxyConfig(host="localhost", http_port=8080, socks_port=1080, username="", password="")
    controller.save_config("proxy", config, create=True)
    controller.record_rejection("proxy")
    controller.update_proxy_runtime("proxy", [1, 2], 99)
    controller.save_config("proxy", config.model_copy(update={"host": "new-host"}))
    proxy = controller.get_proxy("proxy")
    assert proxy.host == "new-host"
    assert proxy.rejected
    assert proxy.operation_timestamps == [1, 2]
    assert proxy.register_cooldown_until == 99
    with pytest.raises(ValueError):
        controller.save_config("proxy", config.model_copy(update={"http_port": 70000}))
    assert controller.get_proxy("proxy") == proxy


def test_profiles_validate_cross_midnight_overlap_and_missing_proxy() -> None:
    ProxyController().save_config(
        "proxy",
        ProxyConfig(host="localhost", http_port=8080, socks_port=1080, username="", password=""),
        create=True,
    )
    controller = ScheduleProfileController()
    profile = ScheduleProfile(
        name_fr="Night", proxy_id="proxy", slots_by_day={"6": [TimeSlot(start="23:00", end="02:00")]}
    )
    controller.save_profile("night", profile, create=True)
    overlap = profile.model_copy(
        update={"slots_by_day": {**profile.slots_by_day, "0": [TimeSlot(start="01:00", end="03:00")]}}
    )
    with pytest.raises(ValueError, match="overlap"):
        controller.save_profile("night", overlap)
    assert controller.get_profile("night") == profile
    short_slot = profile.model_copy(update={"slots_by_day": {"0": [TimeSlot(start="08:00", end="08:15")]}})
    with pytest.raises(ValueError, match="scheduling margins"):
        controller.save_profile("night", short_slot)
    assert controller.get_profile("night") == profile
    with pytest.raises(RuntimeSetupError):
        controller.save_profile("missing", profile.model_copy(update={"proxy_id": "missing"}), create=True)


def test_pin_additions_preserve_existing_codes_and_reject_invalid_batch() -> None:
    pool = PaysafecardPoolController()
    pool.add_pins(["1111 2222 3333 4444"])
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(pool.add_pins, [["1111222233334444"], ["5555666677778888"]]))
    assert pool.load() == ["1111222233334444", "5555666677778888"]
    with pytest.raises(ValueError):
        pool.add_pins(["9999000011112222", "invalid"])
    assert pool.load() == ["1111222233334444", "5555666677778888"]


def test_concurrent_schedule_refreshes_keep_one_set_of_jobs(
    bot_scheduler: BotScheduler, monkeypatch: pytest.MonkeyPatch
) -> None:
    clock = schedule.Scheduler()
    monkeypatch.setattr("src.core.bot.lifecycle.scheduler.schedule", clock)
    profile = ScheduleProfile(
        name_fr="Day", proxy_id="proxy", slots_by_day={"0": [TimeSlot(start="08:00", end="12:00")]}
    )
    reads = Barrier(2)

    def get_profile(_profile_id: str) -> ScheduleProfile:
        # Rendezvous after clearing jobs exposes overlapping rebuilds without the lock.
        try:
            reads.wait(timeout=0.5)
        except BrokenBarrierError:
            pass
        return profile

    monkeypatch.setattr(ScheduleProfileController(), "get_profile", get_profile)
    monkeypatch.setattr(bot_scheduler, "get_bot_config", Mock(return_value=Mock(schedule_profile="day")))
    monkeypatch.setattr(bot_scheduler, "_is_quarantined", lambda: False)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(bot_scheduler.request_configuration_refresh) for _ in range(2)]
        for future in futures:
            future.result(timeout=5)

    assert len(clock.jobs) == 3
    bot_scheduler.stop()
    assert clock.jobs == []
