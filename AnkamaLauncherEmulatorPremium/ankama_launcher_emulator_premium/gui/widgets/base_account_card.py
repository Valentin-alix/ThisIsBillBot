from PyQt6.QtWidgets import QHBoxLayout
from qfluentwidgets import CardWidget, LineEdit

from ankama_launcher_emulator_premium.utils.account_settings import (
    save_account_settings,
)


class BaseAccountCard(CardWidget):
    """Shared proxy input for account cards."""

    def _build_network_widgets(
        self,
        layout: QHBoxLayout,
        proxy_url: str | None,
    ) -> None:
        self._proxy_input = LineEdit()
        self._proxy_input.setPlaceholderText("Proxy (socks5://user:pass@host:port)")
        self._proxy_input.setFixedWidth(300)
        layout.addWidget(self._proxy_input)

        if proxy_url:
            self._proxy_input.setText(proxy_url)

        self._proxy_input.editingFinished.connect(self._save_settings)

    def _settings_key(self) -> str:
        raise NotImplementedError

    def _save_settings(self) -> None:
        save_account_settings(
            self._settings_key(),
            self._proxy_input.text().strip() or None,
        )
