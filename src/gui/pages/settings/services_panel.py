from qfluentwidgets import BodyLabel

from src.controller.settings import SettingsService
from src.core.config import GlobalSettings
from src.gui.pages.settings.settings_panel import SettingsPanel


class ServicesSettingsPanel(SettingsPanel):
    def __init__(self) -> None:
        super().__init__(
            "The Sonji key creates new SmailPro mailboxes. "
            "Previously saved mailboxes remain usable without this key."
        )
        self.summary = BodyLabel("", self)
        self.overview_layout.addWidget(self.summary)
        self.overview_layout.addSpacing(16)
        self.key = self.line("Sonji key")

    def reload(self) -> None:
        def render(settings: GlobalSettings) -> None:
            self.summary.setText(
                "Sonji: " + ("Configured" if SettingsService().sonji_api_key() else "Not configured")
                + (" (variable d’environnement)" if settings.sonji_api_key is None else "")
            )
            self.key.setText(settings.sonji_api_key or "")
            self.key.setEnabled(settings.sonji_api_key is not None)

        self.perform(SettingsService().get, render)

    def save(self) -> None:
        key = self.key.text().strip()
        self.perform(
            lambda: SettingsService().update_sonji_key(key),
            lambda _: self.reload(),
        )
