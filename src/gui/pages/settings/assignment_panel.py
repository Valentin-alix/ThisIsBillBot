from ankama_launcher_emulator.controller.bot_storage import BotStorageController
from ankama_launcher_emulator.controller.schedule_profile import ScheduleProfileController
from ankama_launcher_emulator.interfaces.local_storage import BotRecord
from ankama_launcher_emulator.interfaces.schedule_profile import ScheduleProfile
from PyQt6.QtCore import pyqtSignal

from src.controller.bot_config import BotConfigService
from src.gui.pages.settings.settings_panel import SettingsPanel


class AssignmentSettingsPanel(SettingsPanel):
    changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__(
            "Choose the schedule for an existing account. Active sessions finish with their current schedule."
        )
        self.entries: dict[str, BotRecord] = {}
        self.account = self.overview(["Account", "Email", "Schedule", "Connection", "Status", "Reason"])
        self.profile = self.combo("Schedule")
        self.account.selected.connect(self.select)

    def reload(self) -> None:
        previous = self.account.selected_key
        def render(result: tuple[dict[str, BotRecord], dict[str, ScheduleProfile]]) -> None:
            records, profiles = result
            self.entries = records
            self.profile.clear()
            self.profile.addItems(["None", *sorted(profiles)])
            self.account.set_rows([
                (login, (login, record.email, record.schedule_profile or "None", record.connection_mode,
                         "Quarantined" if record.quarantine_reason else "Registered",
                         record.quarantine_reason or "—"))
                for login, record in sorted(records.items())
            ])
            if previous is None and self.account.selected_key is None and records:
                self.account.select_key(sorted(records)[0])
            self.select()

        self.perform(
            lambda: (
                BotStorageController().get_all_records(),
                ScheduleProfileController().get_all_profiles(),
            ),
            render,
        )

    def select(self) -> None:
        record = self.entries.get(self.account.selected_key or "")
        self.profile.setCurrentIndex(0)
        if record and record.schedule_profile:
            if self.profile.findText(record.schedule_profile) < 0:
                self.profile.addItem(record.schedule_profile)
            self.profile.setCurrentText(record.schedule_profile)
        self.save_button.setEnabled(record is not None and record.quarantine_reason is None)
        self.status.setText(
            "Restore the account from Activity before changing its schedule."
            if record and record.quarantine_reason
            else ""
        )

    def save(self) -> None:
        login = self.account.selected_key or ""
        profile = self.profile.currentText() if self.profile.currentIndex() > 0 else None

        def done(_: None) -> None:
            self.changed.emit()
            self.reload()

        self.perform(lambda: BotConfigService().assign_schedule_profile(login, profile), done)
