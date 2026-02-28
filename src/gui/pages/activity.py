from typing import cast

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QHBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    ComboBox,
    FluentIcon,
    PrimaryPushButton,
    PushButton,
    SubtitleLabel,
    TableWidget,
)
from qfluentwidgets.components.dialog_box.dialog import MessageBox
from qfluentwidgets.components.widgets.label import StrongBodyLabel

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.bot_storage import (
    BotStorageController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.mail_account import (
    MailAccountController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.quarantine_signals import (
    quarantine_signals,
)
from src.services.background import run_in_background
from src.services.user_activity import UserActivityEntry, UserActivityService

QuarantineRow = tuple[str, str, str]


class ActivityPage(QWidget):
    restore_account_requested = pyqtSignal(str)
    delete_account_requested = pyqtSignal(str)
    restore_mailbox_requested = pyqtSignal(str)
    delete_mailbox_requested = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._activity_service = UserActivityService()
        self._activity_entries: tuple[UserActivityEntry, ...] | None = None
        self._quarantined: list[QuarantineRow] | None = None
        self._selected_target: tuple[str, str] | None = None
        self._quarantine_refresh_pending = False
        self.setObjectName("activity")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(SubtitleLabel("Activité", self))
        layout.addWidget(
            BodyLabel(
                "Suivez les événements récents et décidez des suites à donner aux éléments en quarantaine.",
                self,
            )
        )
        layout.addWidget(self._create_activity_card(), 3)
        layout.addWidget(self._create_quarantine_card(), 2)

        self._activity_service.signals.entry_added.connect(self._on_activity_entry_added)
        quarantine_signals.changed.connect(self._on_quarantine_changed)

    def _create_activity_card(self) -> CardWidget:
        card = CardWidget(self)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.addWidget(StrongBodyLabel("Historique récent", card))
        header.addStretch()
        header.addWidget(BodyLabel("Compte", card))
        self.login_filter = ComboBox(card)
        self.login_filter.setMinimumWidth(190)
        self.login_filter.currentIndexChanged.connect(self._render_activity)
        header.addWidget(self.login_filter)
        layout.addLayout(header)

        self.activity_table = self._create_table(card, ["Date", "Compte", "Niveau", "Événement"])
        self.activity_table.setMinimumHeight(220)
        layout.addWidget(self.activity_table)
        return card

    def _create_quarantine_card(self) -> CardWidget:
        card = CardWidget(self)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.addWidget(StrongBodyLabel("Éléments en quarantaine", card))
        header.addStretch()
        header.addWidget(BodyLabel("Aucune action n’est effectuée sans confirmation.", card))
        layout.addLayout(header)

        self.quarantine_table = self._create_table(card, ["Type", "Identifiant", "Motif"])
        self.quarantine_table.setMinimumHeight(160)
        self.quarantine_table.itemSelectionChanged.connect(self._select_quarantine)
        layout.addWidget(self.quarantine_table)

        actions = QHBoxLayout()
        actions.addStretch()
        self.restore_button = PrimaryPushButton(FluentIcon.SYNC, "Réactiver", card)
        self.restore_button.clicked.connect(self._restore_selected)
        self.delete_button = PushButton(FluentIcon.DELETE, "Supprimer", card)
        self.delete_button.clicked.connect(self._delete_selected)
        actions.addWidget(self.restore_button)
        actions.addWidget(self.delete_button)
        layout.addLayout(actions)
        return card

    def showEvent(self, a0: QShowEvent | None) -> None:
        self.refresh()
        super().showEvent(a0)

    @staticmethod
    def _create_table(parent: QWidget, headers: list[str]) -> TableWidget:
        table = TableWidget(parent)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        vertical_header = table.verticalHeader()
        horizontal_header = table.horizontalHeader()
        assert vertical_header is not None
        assert horizontal_header is not None
        vertical_header.setVisible(False)
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        horizontal_header.setStretchLastSection(True)
        return table

    @staticmethod
    def _set_table_rows(table: TableWidget, rows: list[tuple[str, ...]]) -> None:
        table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                table.setItem(row, column, QTableWidgetItem(value))

    def refresh(self) -> None:
        self._refresh_activity()
        self._refresh_quarantined()

    def _on_activity_entry_added(self) -> None:
        if self.isVisible():
            self._refresh_activity()

    def _on_quarantine_changed(self) -> None:
        if self.isVisible():
            self._refresh_quarantined()

    def _refresh_activity(self) -> None:
        entries = self._activity_service.recent()
        if entries == self._activity_entries:
            return
        current_login = cast(str | None, self.login_filter.currentData())
        self._activity_entries = entries
        self._refresh_login_filter(current_login)
        self._render_activity()

    def _refresh_login_filter(self, current_login: str | None) -> None:
        assert self._activity_entries is not None
        logins = sorted({entry.login for entry in self._activity_entries if entry.login is not None})
        self.login_filter.blockSignals(True)
        self.login_filter.clear()
        self.login_filter.addItem("Tous", userData=None)
        for login in logins:
            self.login_filter.addItem(login, userData=login)
        self.login_filter.setCurrentIndex(max(self.login_filter.findData(current_login), 0))
        self.login_filter.blockSignals(False)

    def _render_activity(self) -> None:
        if self._activity_entries is None:
            return
        selected_login = cast(str | None, self.login_filter.currentData())
        rows = [
            (
                entry.happened_at.astimezone().strftime("%d/%m %H:%M:%S"),
                entry.login or "Application",
                entry.severity,
                entry.message,
            )
            for entry in self._activity_entries
            if selected_login is None or entry.login == selected_login
        ]
        self.activity_table.setUpdatesEnabled(False)
        self._set_table_rows(self.activity_table, rows)
        self.activity_table.setUpdatesEnabled(True)
        QTimer.singleShot(0, self.activity_table.scrollToBottom)

    def _refresh_quarantined(self) -> None:
        if self._quarantine_refresh_pending:
            return
        self._quarantine_refresh_pending = True
        run_in_background(
            lambda _: self._load_quarantined(),
            on_success=self._render_quarantined,
            on_error=self._on_quarantine_load_error,
            parent=self,
        )

    @staticmethod
    def _load_quarantined() -> list[QuarantineRow]:
        quarantined: list[QuarantineRow] = []
        for login, record in BotStorageController().get_all_records().items():
            if record.quarantine_reason is not None:
                quarantined.append(("Compte", login, record.quarantine_reason))
        for email, entry in MailAccountController().get_all_entries().items():
            if entry.quarantine_reason is not None:
                quarantined.append(("Mailbox", email, entry.quarantine_reason))
        return quarantined

    def _render_quarantined(self, result: object) -> None:
        quarantined = cast(list[QuarantineRow], result)
        self._quarantine_refresh_pending = False
        if quarantined == self._quarantined:
            return
        self._quarantined = quarantined
        selected_row = next(
            (
                row
                for row, (kind, identifier, _) in enumerate(quarantined)
                if (kind, identifier) == self._selected_target
            ),
            None,
        )
        self._selected_target = (
            (quarantined[selected_row][0], quarantined[selected_row][1]) if selected_row is not None else None
        )

        self.quarantine_table.blockSignals(True)
        self._set_table_rows(self.quarantine_table, quarantined)
        if selected_row is not None:
            self.quarantine_table.selectRow(selected_row)
        self.quarantine_table.blockSignals(False)
        self._set_action_enabled()

    def _on_quarantine_load_error(self, _: object) -> None:
        self._quarantine_refresh_pending = False

    def _select_quarantine(self) -> None:
        row = self.quarantine_table.currentRow()
        if row < 0:
            self._selected_target = None
        else:
            assert self._quarantined is not None
            kind, identifier, _ = self._quarantined[row]
            self._selected_target = kind, identifier
        self._set_action_enabled()

    def _set_action_enabled(self) -> None:
        enabled = self._selected_target is not None
        self.restore_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def _restore_selected(self) -> None:
        if self._selected_target is None:
            return
        kind, identifier = self._selected_target
        if kind == "Compte":
            self.restore_account_requested.emit(identifier)
        else:
            self.restore_mailbox_requested.emit(identifier)
        self.refresh()

    def _delete_selected(self) -> None:
        if self._selected_target is None:
            return
        kind, identifier = self._selected_target
        confirmation = MessageBox(
            "Supprimer définitivement",
            f"Supprimer définitivement {identifier} ? Cette action est irréversible.",
            self,
        )
        confirmation.yesButton.setText("Supprimer")
        confirmation.cancelButton.setText("Annuler")
        if not confirmation.exec():
            return
        if kind == "Compte":
            self.delete_account_requested.emit(identifier)
        else:
            self.delete_mailbox_requested.emit(identifier)
        self.refresh()
