from collections.abc import Iterator
from pathlib import Path
from time import monotonic
from typing import cast
from unittest.mock import Mock

import pytest
from PyQt6.QtCore import QEventLoop, QTime, QTimer
from PyQt6.QtWidgets import QLineEdit, QAbstractButton
from qfluentwidgets.components.dialog_box.dialog import MessageBox

from ankama_launcher_emulator.controller.mail_account import MailAccountController
from ankama_launcher_emulator.controller.bot_storage import BotStorageController
from ankama_launcher_emulator.controller.proxy import ProxyController
from ankama_launcher_emulator.controller.schedule_profile import ScheduleProfileController
from ankama_launcher_emulator.controller.paysafecard_pool import PaysafecardPoolController
from ankama_launcher_emulator.interfaces.mail_account import ImapAccountConfig, ManualAccountConfig
from ankama_launcher_emulator.interfaces.local_storage import BotRecord
from ankama_launcher_emulator.interfaces.schedule_profile import ProxyConfig, ScheduleProfile, TimeSlot
from src.controller.settings import SettingsService
from src.core.bot.bot_manager import BotManager
from src.core.bot.bot import Bot
from src.gui.pages.settings.settings_page import SettingsPage
from src.gui.pages.settings.settings_panel import SettingsPanel
from src.gui.pages.settings.settings_overview import SettingsOverview
from src.services import background


def _process_events() -> None:
    loop = QEventLoop()
    QTimer.singleShot(10, loop.quit)
    loop.exec()


def wait_ready(panel: SettingsPanel) -> None:
    deadline = monotonic() + 10
    while not panel.isEnabled() or background._running:
        assert monotonic() < deadline, "GUI task did not complete"
        _process_events()


def overview_rows(overview: SettingsOverview) -> list[list[str]]:
    result: list[list[str]] = []
    for row in range(overview.table.rowCount()):
        values: list[str] = []
        for column in range(overview.table.columnCount() - 1):
            item = overview.table.item(row, column)
            assert item is not None
            values.append(item.text())
        result.append(values)
    return result


@pytest.fixture
def page(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[SettingsPage]:
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
    monkeypatch.setattr(
        "ankama_launcher_emulator.controller.bot_storage.BOTS_STORAGE_PATH", tmp_path / "bots.json"
    )
    widget = SettingsPage()
    widget.resize(1100, 850)
    widget.show()
    wait_ready(widget.behaviors)
    yield widget
    wait_ready(widget.behaviors)
    widget.close()
    widget.deleteLater()
    _process_events()


def test_gui_saves_and_reloads_global_choices_and_key(page: SettingsPage) -> None:
    panel = page.behaviors
    panel.checks["do_craft"].setChecked(True)
    panel.checks["do_fighter"].setChecked(False)
    panel.automation.setChecked(True)
    panel.save_button.click()
    wait_ready(panel)
    assert SettingsService().get().behaviors.do_craft
    assert not SettingsService().get().behaviors.do_fighter
    assert SettingsService().get().enable_account_automation
    panel.checks["do_craft"].setChecked(False)
    panel.cancel_button.click()
    wait_ready(panel)
    assert panel.checks["do_craft"].isChecked()
    SettingsService().update_sonji_key("")
    page.navigation.widget("5").click()
    assert page.stack.currentIndex() == 5
    wait_ready(page.services)
    assert page.services.summary.text() == "Sonji: Not configured"
    page.services.key.setText("local-service-key")
    assert page.services.summary.text() == "Sonji: Not configured"
    page.services.save_button.click()
    wait_ready(page.services)
    assert SettingsService().sonji_api_key() == "local-service-key"
    assert page.services.summary.text() == "Sonji: Configured"


def test_gui_email_validation_and_manual_and_imap_roundtrip(page: SettingsPage) -> None:
    page.navigation.widget("1").click()
    assert page.stack.currentIndex() == 1
    panel = page.mail
    wait_ready(panel)
    panel.provider.setCurrentText("manual")
    panel.email.setText("invalid")
    panel.save_button.click()
    wait_ready(panel)
    assert "Invalid" in panel.status.text()
    assert MailAccountController().get_all_entries() == {}
    panel.email.setText("manual@example.com")
    panel.save_button.click()
    wait_ready(panel)
    assert isinstance(MailAccountController().get_config("manual@example.com"), ManualAccountConfig)
    panel.selection.table.selectRow(0)
    assert panel.email.isReadOnly()
    panel.provider.setCurrentText("imap")
    panel.host.setText("imap.example.com")
    panel.username.setText("manual@example.com")
    panel.password.setText("test-password")
    assert panel.password.echoMode() == QLineEdit.EchoMode.Normal
    panel.save_button.click()
    wait_ready(panel)
    config = MailAccountController().get_config("manual@example.com")
    assert isinstance(config, ImapAccountConfig)
    assert config.host == "imap.example.com"
    assert config.password == "test-password"


def test_gui_proxy_planning_and_payment_forms(page: SettingsPage) -> None:
    page.navigation.widget("2").click()
    assert page.stack.currentIndex() == 2
    proxy = page.proxies
    wait_ready(proxy)
    proxy.identifier.setText("proxy-1")
    proxy.host.setText("localhost")
    proxy.http_port.setText("8080")
    proxy.socks_port.setText("1080")
    assert proxy.password.echoMode() == QLineEdit.EchoMode.Normal
    proxy.save_button.click()
    wait_ready(proxy)
    assert ProxyController().get_proxy("proxy-1").http_port == 8080
    page.navigation.widget("3").click()
    assert page.stack.currentIndex() == 3
    profile = page.schedules
    wait_ready(profile)
    profile.identifier.setText("night")
    profile.name.setText("Night session")
    profile.proxy.setCurrentText("proxy-1")
    profile.days[0].add_button.click()
    profile.days[0].rows[0].start.setTime(QTime(22, 0))
    profile.days[0].rows[0].end.setTime(QTime(3, 0))
    _process_events()
    assert profile.days[0].rows[0].overnight.isVisible()
    profile.save_button.click()
    wait_ready(profile)
    saved = ScheduleProfileController().get_profile("night")
    assert saved is not None
    assert saved.slots_by_day["0"][0].end == "03:00"
    assert overview_rows(profile.selection) == [
        ["night", "Night session", "proxy-1", "Mon: 22:00–03:00 (+1 day)"]
    ]
    page.navigation.widget("6").click()
    assert page.stack.currentIndex() == 6
    payment = page.payments
    wait_ready(payment)
    payment.pin.setText("1111222233334444")
    payment.save_button.click()
    wait_ready(payment)
    assert PaysafecardPoolController().load() == ["1111222233334444"]
    assert payment.pin.text() == ""
    assert payment.count.text() == "1"
    assert overview_rows(payment.selection) == [["1", "1111 2222 3333 4444"]]


def test_gui_schedule_edits_roundtrip_and_cancel(page: SettingsPage) -> None:
    ProxyController().save_config(
        "proxy", ProxyConfig(host="localhost", http_port=8080, socks_port=1080, username="", password=""),
        create=True,
    )
    page.navigation.widget("3").click()
    panel = page.schedules
    wait_ready(panel)
    panel.identifier.setText("week")
    panel.name.setText("Week")
    monday = panel.days[0]
    assert monday.empty.isVisible()
    monday.add_button.click()
    monday.add_button.click()
    monday.rows[1].start.setTime(QTime(14, 0))
    monday.rows[1].end.setTime(QTime(18, 0))
    expected = [TimeSlot(start="08:00", end="12:00"), TimeSlot(start="14:00", end="18:00")]
    panel.save_button.click()
    wait_ready(panel)
    panel.selection.table.selectRow(0)
    assert monday.values() == expected
    assert panel.days[1].values() == []
    monday.rows[0].remove_button.click()
    panel.cancel_button.click()
    wait_ready(panel)
    assert panel.selection.selected_key == "week"
    assert monday.values() == expected
    for row in monday.rows[:]:
        row.remove_button.click()
    assert monday.empty.isVisible()
    panel.save_button.click()
    wait_ready(panel)
    saved = ScheduleProfileController().get_profile("week")
    assert saved is not None and saved.slots_by_day["0"] == []


@pytest.mark.parametrize("end, message", [(QTime(9, 0), "exceed one hour"), (QTime(8, 0), "exceed one hour"), (QTime(12, 0), "overlap")])
def test_gui_schedule_validation_keeps_input(page: SettingsPage, end: QTime, message: str) -> None:
    ProxyController().save_config(
        "proxy", ProxyConfig(host="localhost", http_port=8080, socks_port=1080, username="", password=""),
        create=True,
    )
    page.navigation.widget("3").click()
    panel = page.schedules
    wait_ready(panel)
    panel.identifier.setText("invalid")
    panel.name.setText("Schedule")
    panel.days[0].add_button.click()
    panel.days[0].rows[0].end.setTime(end)
    if message == "overlap":
        panel.days[6].add_slot(TimeSlot(start="22:00", end="09:00"))
    panel.save_button.click()
    wait_ready(panel)
    assert message in panel.status.text()
    assert panel.days[0].rows[0].end.time() == end
    assert panel.identifier.text() == "invalid"
    assert ScheduleProfileController().get_profile("invalid") is None


def test_gui_assigns_existing_account_and_handles_account_removed_while_editing(page: SettingsPage) -> None:
    storage = BotStorageController()
    storage.upsert_record(
        "existing@example.com",
        lambda: BotRecord(email="existing@example.com", hardware_id="hw"),
        lambda _: None,
    )
    ProxyController().save_config(
        "proxy",
        ProxyConfig(host="localhost", http_port=8080, socks_port=1080, username="", password=""),
        create=True,
    )
    ScheduleProfileController().save_profile(
        "planning", ScheduleProfile(name_fr="Schedule", proxy_id="proxy", slots_by_day={}), create=True
    )
    page.navigation.widget("4").click()
    assert page.stack.currentIndex() == 4
    panel = page.assignments
    wait_ready(panel)
    panel.profile.setCurrentText("planning")
    panel.save_button.click()
    wait_ready(panel)
    record = storage.get_record("existing@example.com")
    assert record is not None and record.schedule_profile == "planning"
    storage.remove_record("existing@example.com")
    panel.save_button.click()
    wait_ready(panel)
    assert "no longer exists" in panel.status.text()


def test_overviews_refresh_on_open_and_preserve_selection(page: SettingsPage) -> None:
    page.navigation.widget("1").click()
    panel = page.mail
    wait_ready(panel)
    assert panel.selection.empty.isVisible()
    assert overview_rows(panel.selection) == []
    controller = MailAccountController()
    controller.save_config("b@example.com", ManualAccountConfig(), create=True)
    panel.cancel_button.click()
    wait_ready(panel)
    panel.selection.table.selectRow(0)
    assert panel.email.text() == "b@example.com"
    controller.save_config("a@example.com", ManualAccountConfig(), create=True)
    panel.cancel_button.click()
    wait_ready(panel)
    assert panel.selection.selected_key == "b@example.com"
    assert panel.email.text() == "b@example.com"
    assert overview_rows(panel.selection) == [
        ["a@example.com", "manual", "Available"],
        ["b@example.com", "manual", "Available"],
    ]
    panel.selection.new_button.click()
    assert not panel.email.isReadOnly()
    assert panel.email.text() == ""
    page.navigation.widget("6").click()
    wait_ready(page.payments)
    assert page.payments.selection.empty.isVisible()
    page.navigation.widget("1").click()
    wait_ready(panel)
    PaysafecardPoolController().add_pins(["9999888877776666", "1111222233334444"])
    page.navigation.widget("6").click()
    wait_ready(page.payments)
    assert overview_rows(page.payments.selection) == [
        ["1", "9999 8888 7777 6666"], ["2", "1111 2222 3333 4444"]
    ]


def test_account_overview_quarantine_and_removal(page: SettingsPage) -> None:
    storage = BotStorageController()
    storage.upsert_record(
        "quarantined", lambda: BotRecord(
            email="account@example.com", hardware_id="hw", quarantine_reason="Suspended account"
        ), lambda _: None,
    )
    page.navigation.widget("4").click()
    panel = page.assignments
    wait_ready(panel)
    assert overview_rows(panel.account) == [
        ["quarantined", "account@example.com", "None", "socket", "Quarantined", "Suspended account"]
    ]
    assert not panel.save_button.isEnabled()
    storage.remove_record("quarantined")
    panel.cancel_button.click()
    wait_ready(panel)
    assert panel.account.selected_key is None
    assert panel.account.empty.isVisible()
    assert not panel.save_button.isEnabled()


def delete_row(overview: SettingsOverview, row: int, *, confirm: bool = True) -> None:
    button = overview.table.cellWidget(row, overview.table.columnCount() - 1)
    assert isinstance(button, QAbstractButton)

    def answer() -> None:
        window = overview.window()
        assert window is not None
        dialogs = window.findChildren(MessageBox)
        dialog = next(dialog for dialog in dialogs if dialog.isVisible())
        if confirm:
            dialog.yesButton.click()
        else:
            dialog.cancelButton.click()

    QTimer.singleShot(0, answer)
    button.click()


def test_payment_delete_confirmation_targets_its_row(page: SettingsPage) -> None:
    pool = PaysafecardPoolController()
    pool.add_pins(["1111222233334444", "5555666677778888"])
    page.navigation.widget("6").click()
    panel = page.payments
    wait_ready(panel)
    panel.selection.table.selectRow(1)
    delete_row(panel.selection, 0, confirm=False)
    assert len(pool.load()) == 2
    delete_row(panel.selection, 0)
    wait_ready(panel)
    assert pool.load() == ["5555666677778888"]
    assert panel.selection.selected_key == "5555666677778888"
    delete_row(panel.selection, 0)
    wait_ready(panel)
    assert pool.load() == []
    assert panel.selection.empty.isVisible()


@pytest.mark.parametrize("quarantined", [False, True])
def test_delete_used_planning_and_proxy_refused_then_allowed(page: SettingsPage, quarantined: bool) -> None:
    proxies = ProxyController()
    profiles = ScheduleProfileController()
    storage = BotStorageController()
    proxies.save_config("proxy", ProxyConfig(host="localhost", http_port=8080, socks_port=1080, username="", password=""), create=True)
    profiles.save_profile("week", ScheduleProfile(name_fr="Semaine", proxy_id="proxy", slots_by_day={}), create=True)
    page.navigation.widget("3").click()
    panel = page.schedules
    wait_ready(panel)
    panel.selection.table.selectRow(0)
    # Add the reference after loading the table to exercise deletion-time validation.
    storage.upsert_record("account", lambda: BotRecord(
        email="account@example.com", hardware_id="hw",
        schedule_profile=None if quarantined else "week",
        quarantined_schedule_profile="week" if quarantined else None,
        quarantine_reason="Suspendu" if quarantined else None,
    ), lambda _: None)
    delete_row(panel.selection, 0)
    wait_ready(panel)
    assert "account" in panel.status.text()
    assert profiles.get_profile("week") is not None
    assert panel.selection.selected_key == "week"
    page.navigation.widget("2").click()
    wait_ready(page.proxies)
    delete_row(page.proxies.selection, 0)
    wait_ready(page.proxies)
    assert "week" in page.proxies.status.text()
    assert "proxy" in proxies.get_all()
    storage.remove_record("account")
    page.navigation.widget("3").click()
    wait_ready(panel)
    delete_row(panel.selection, 0)
    wait_ready(panel)
    assert profiles.get_all_profiles() == {}
    assert panel.identifier.text() == ""
    assert not panel.identifier.isReadOnly()
    page.navigation.widget("2").click()
    wait_ready(page.proxies)
    delete_row(page.proxies.selection, 0)
    wait_ready(page.proxies)
    assert proxies.get_all() == {}


def test_account_and_mail_delete_use_manager(page: SettingsPage, monkeypatch: pytest.MonkeyPatch) -> None:
    storage = BotStorageController()
    storage.upsert_record("account", lambda: BotRecord(email="account@example.com", hardware_id="hw"), lambda _: None)
    MailAccountController().save_config("account@example.com", ManualAccountConfig(), create=True)
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
    panel = page.assignments
    panel.bind_deletion(panel.account, manager.delete_account, background=False)
    page.mail.bind_deletion(page.mail.selection, manager.delete_mailbox, background=False)
    page.navigation.widget("4").click()
    wait_ready(panel)
    delete_row(panel.account, 0)
    wait_ready(panel)
    assert storage.get_record("account") is None
    bot.bot_signals.stop.emit.assert_called_once_with()
    remove_key.assert_called_once_with("account")
    remove_snapshot.assert_called_once_with("account")
    synchronized.assert_called_once_with()
    assert panel.account.empty.isVisible()
    assert MailAccountController().get_config("account@example.com") is not None
    page.navigation.widget("1").click()
    wait_ready(page.mail)
    delete_row(page.mail.selection, 0)
    wait_ready(page.mail)
    assert MailAccountController().get_all_entries() == {}
    assert page.mail.selection.empty.isVisible()
