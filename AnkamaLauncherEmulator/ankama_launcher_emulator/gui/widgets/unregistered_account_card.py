from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel
from qfluentwidgets import BodyLabel, PrimaryPushButton

from ankama_launcher_emulator.gui.consts import ORANGE_HEXA
from ankama_launcher_emulator.gui.widgets.base_account_card import BaseAccountCard


class UnregisteredAccountCard(BaseAccountCard):
    authenticate_requested = pyqtSignal(
        object, object
    )  # (interface_ip: str | None, proxy_url: str | None)

    def __init__(
        self,
        email: str,
        password: str,
        all_interface: dict[str, tuple[str, str]],
        interface_ip: str | None = None,
        proxy_url: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.email = email
        self._password = password
        self._setup_ui(all_interface, interface_ip, proxy_url)

    def _settings_key(self) -> str:
        return self.email

    def _setup_ui(
        self,
        all_interface: dict[str, tuple[str, str]],
        interface_ip: str | None,
        proxy_url: str | None,
    ) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"background-color: {ORANGE_HEXA}; border-radius: 5px;")
        layout.addWidget(dot)

        layout.addWidget(BodyLabel(self.email), 1)

        self._build_network_widgets(layout, all_interface, interface_ip, proxy_url)

        self._badge = BodyLabel("Not authenticated")
        self._badge.setStyleSheet(f"color: {ORANGE_HEXA};")
        layout.addWidget(self._badge)

        self._auth_btn = PrimaryPushButton("Authenticate")
        self._auth_btn.setFixedWidth(130)
        self._auth_btn.clicked.connect(self._on_auth_clicked)
        layout.addWidget(self._auth_btn)

    def _on_auth_clicked(self) -> None:
        interface_ip = self._ip_combo.currentData() or None
        proxy_url = self._proxy_input.text().strip() or None
        self.set_authenticating(True)
        self.authenticate_requested.emit(interface_ip, proxy_url)

    def set_authenticating(self, value: bool) -> None:
        self._auth_btn.setEnabled(not value)
        self._ip_combo.setEnabled(not value)
        self._proxy_input.setEnabled(not value)
        self._badge.setText("Authenticating..." if value else "Not authenticated")
