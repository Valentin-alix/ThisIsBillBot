from ankama_launcher_emulator.interfaces.schedule_profile import TimeSlot
from PyQt6.QtCore import QTime
from PyQt6.QtWidgets import QHBoxLayout, QTimeEdit, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget, PushButton


class TimeSlotEditor(QWidget):
    def __init__(self, day: str, slot: TimeSlot, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.start = QTimeEdit(QTime.fromString(slot.start, "HH:mm"), self)
        self.end = QTimeEdit(QTime.fromString(slot.end, "HH:mm"), self)
        for label, editor in (("Start", self.start), ("End", self.end)):
            editor.setDisplayFormat("HH:mm")
            editor.setMinimumHeight(32)
            editor.setAccessibleName(f"{day} — {label}")
            layout.addWidget(BodyLabel(label, self))
            layout.addWidget(editor)
        self.overnight = BodyLabel("Ends the next day", self)
        layout.addWidget(self.overnight)
        layout.addStretch()
        self.remove_button = PushButton("Remove", self)
        self.remove_button.setAccessibleName(f"Remove {day.lower()} time slot")
        layout.addWidget(self.remove_button)
        self.start.timeChanged.connect(self.update_overnight)
        self.end.timeChanged.connect(self.update_overnight)
        self.update_overnight()

    def update_overnight(self) -> None:
        self.overnight.setVisible(self.end.time() < self.start.time())

    def value(self) -> TimeSlot:
        return TimeSlot(start=self.start.time().toString("HH:mm"), end=self.end.time().toString("HH:mm"))


class ScheduleDayEditor(CardWidget):
    def __init__(self, day: str, parent: QWidget) -> None:
        super().__init__(parent)
        self.day = day
        self.rows: list[TimeSlotEditor] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        header = QHBoxLayout()
        title = BodyLabel(day, self)
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        header.addWidget(title)
        header.addStretch()
        self.add_button = PushButton("Add time slot", self)
        self.add_button.setAccessibleName(f"Add a time slot on {day.lower()}")
        header.addWidget(self.add_button)
        layout.addLayout(header)
        self.empty = BodyLabel("No time slots", self)
        layout.addWidget(self.empty)
        self.slots_layout = QVBoxLayout()
        self.slots_layout.setSpacing(12)
        layout.addLayout(self.slots_layout)
        self.add_button.clicked.connect(lambda: self.add_slot(TimeSlot(start="08:00", end="12:00")))

    def add_slot(self, slot: TimeSlot) -> None:
        row = TimeSlotEditor(self.day, slot, self)
        self.rows.append(row)
        self.slots_layout.addWidget(row)
        row.remove_button.clicked.connect(lambda: self.remove_slot(row))
        self.empty.hide()

    def remove_slot(self, row: TimeSlotEditor) -> None:
        self.rows.remove(row)
        self.slots_layout.removeWidget(row)
        row.hide()
        row.deleteLater()
        self.empty.setVisible(not self.rows)

    def set_slots(self, slots: list[TimeSlot]) -> None:
        for row in self.rows[:]:
            self.remove_slot(row)
        for slot in slots:
            self.add_slot(slot)

    def values(self) -> list[TimeSlot]:
        return [row.value() for row in self.rows]
