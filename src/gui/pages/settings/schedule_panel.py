from ankama_launcher_emulator.controller.proxy import ProxyController
from ankama_launcher_emulator.controller.schedule_profile import ScheduleProfileController
from ankama_launcher_emulator.interfaces.schedule_profile import PersistedProxy, ScheduleProfile
from PyQt6.QtCore import pyqtSignal

from src.controller.settings_deletion import delete_schedule
from src.gui.pages.settings.settings_panel import SettingsPanel
from src.gui.pages.settings.schedule_day_editor import ScheduleDayEditor


class ScheduleSettingsPanel(SettingsPanel):
    changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__(
            "Add each day's time slots with a start and end time. "
            "Each slot must exceed one hour and may cross midnight. Changes preserve active sessions."
        )
        self.entries: dict[str, ScheduleProfile] = {}
        self.selection = self.overview(["Identifier", "Name", "Proxy", "Time slots"], "New schedule…")
        self.identifier = self.line("Identifier")
        self.name = self.line("Name")
        self.proxy = self.combo("Proxy")
        self.days = [
            ScheduleDayEditor(day, self)
            for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
        ]
        for day in self.days:
            self.form.addRow(day)
        self.selection.selected.connect(self.select)
        self.bind_deletion(self.selection, delete_schedule, self.changed.emit)

    def reload(self) -> None:
        def render(result: tuple[dict[str, ScheduleProfile], dict[str, PersistedProxy]]) -> None:
            profiles, proxies = result
            self.entries = profiles
            self.proxy.clear()
            self.proxy.addItems(sorted(proxies))
            self.selection.set_rows([
                (identifier, (identifier, profile.name_fr, profile.proxy_id,
                    "\n".join(
                        f"{day}: " + ", ".join(
                            f"{slot.start}–{slot.end}" + (" (+1 day)" if slot.end < slot.start else "")
                            for slot in profile.slots_by_day.get(str(index), [])
                        )
                        for index, day in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))
                        if profile.slots_by_day.get(str(index))
                    ) or "No time slots"))
                for identifier, profile in sorted(profiles.items())
            ])
            self.select()

        self.perform(
            lambda: (ScheduleProfileController().get_all_profiles(), ProxyController().get_all()), render
        )

    def select(self) -> None:
        identifier = self.selection.selected_key or ""
        profile = self.entries.get(identifier)
        self.identifier.setText(identifier)
        self.identifier.setReadOnly(profile is not None)
        self.name.setText(profile.name_fr if profile else "")
        if profile:
            if self.proxy.findText(profile.proxy_id) < 0:
                self.proxy.addItem(profile.proxy_id)
            self.proxy.setCurrentText(profile.proxy_id)
        for index, widget in enumerate(self.days):
            widget.set_slots(profile.slots_by_day.get(str(index), []) if profile else [])

    def save(self) -> None:
        slots = {str(index): widget.values() for index, widget in enumerate(self.days)}
        profile = ScheduleProfile(
            name_fr=self.name.text().strip(), proxy_id=self.proxy.currentText(), slots_by_day=slots
        )
        identifier = self.identifier.text().strip()
        create = self.selection.selected_key is None

        def done(_: None) -> None:
            self.changed.emit()
            self.reload()

        self.perform(
            lambda: ScheduleProfileController().save_profile(identifier, profile, create=create), done
        )
