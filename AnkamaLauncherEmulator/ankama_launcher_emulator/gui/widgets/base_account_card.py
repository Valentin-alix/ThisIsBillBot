from PyQt6.QtWidgets import QHBoxLayout
from qfluentwidgets import CardWidget, ComboBox, LineEdit

from ankama_launcher_emulator.utils.account_settings import save_account_settings


class BaseAccountCard(CardWidget):
    """Shared network-selection widgets (interface combo + proxy input) for account cards."""

    def _build_network_widgets(
        self,
        layout: QHBoxLayout,
        all_interface: dict[str, tuple[str, str]],
        interface_ip: str | None,
        proxy_url: str | None,
    ) -> None:
        self._ip_combo = ComboBox()
        self._ip_combo.addItem("Auto", userData=None)
        self._ip_combo.setFixedWidth(300)
        for ip_value, (display_name, public_ip) in all_interface.items():
            self._ip_combo.addItem(f"{display_name}\t{public_ip}", userData=ip_value)
        layout.addWidget(self._ip_combo)

        self._proxy_input = LineEdit()
        self._proxy_input.setPlaceholderText("Proxy (socks5://user:pass@host:port)")
        self._proxy_input.setFixedWidth(300)
        layout.addWidget(self._proxy_input)

        if interface_ip is not None:
            idx = self._ip_combo.findData(interface_ip)
            if idx >= 0:
                self._ip_combo.setCurrentIndex(idx)
        if proxy_url:
            self._proxy_input.setText(proxy_url)

        self._ip_combo.currentIndexChanged.connect(lambda _: self._save_settings())
        self._proxy_input.editingFinished.connect(self._save_settings)

    def _settings_key(self) -> str:
        raise NotImplementedError

    def _save_settings(self) -> None:
        save_account_settings(
            self._settings_key(),
            self._ip_combo.currentData() or None,
            self._proxy_input.text().strip() or None,
        )

    def update_interfaces(self, all_interface: dict[str, tuple[str, str]]) -> None:
        current_data = self._ip_combo.currentData()
        self._ip_combo.clear()
        self._ip_combo.addItem("Auto", userData=None)
        for ip_value, (display_name, public_ip) in all_interface.items():
            self._ip_combo.addItem(f"{display_name}\t{public_ip}", userData=ip_value)
        if current_data is not None:
            idx = self._ip_combo.findData(current_data)
            if idx >= 0:
                self._ip_combo.setCurrentIndex(idx)
