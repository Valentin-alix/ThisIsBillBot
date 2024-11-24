from typing import Callable, cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel

from ankama_launcher_emulator.gui.consts import RED_HEXA
from ankama_launcher_emulator.gui.utils import run_in_background
from ankama_launcher_emulator.gui.widgets.account_card import AccountCard
from ankama_launcher_emulator.gui.widgets.download_banner import DownloadBanner
from ankama_launcher_emulator.utils.account_settings import load_account_settings


class GamePage(QWidget):
    """Scrollable list of AccountCards with a download progress banner."""

    def __init__(
        self,
        accounts: list,
        all_interface: dict[str, tuple[str, str]],
        launch: Callable,
        on_success: Callable[[str], None],
        on_error: Callable[[str], None],
        parent=None,
    ):
        super().__init__(parent)
        self._launch = launch
        self._on_success = on_success
        self._on_error = on_error
        self._cards: list[AccountCard] = []
        self._setup_ui(accounts, all_interface)

    def _setup_ui(self, accounts: list, all_interface: dict) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)

        self._banner = DownloadBanner()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        self._cards_layout = QVBoxLayout(container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(8)

        for account in accounts:
            self._append_card(account, all_interface, container)

        self._cards_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(self._banner)
        layout.addWidget(scroll, 1)

    def _append_card(self, account: dict, all_interface: dict, parent=None) -> AccountCard:
        login = account["apikey"]["login"]
        saved_ip, saved_proxy = load_account_settings(login)
        card = AccountCard(login, all_interface, parent, interface_ip=saved_ip, proxy_url=saved_proxy)
        card.launch_requested.connect(self._make_launch_handler(login, card))
        card.error_occurred.connect(self._on_error)
        self._cards.append(card)
        return card

    def _set_panel_status(self, text: str) -> None:
        was_visible = self._banner.isVisible()
        self._banner.set_status(text)
        if not text:
            for card in self._cards:
                card.set_launch_enabled(True)
        elif not was_visible:
            for card in self._cards:
                card.set_launch_enabled(False)

    def _make_launch_handler(
        self, login: str, card: AccountCard
    ) -> Callable[[object, object], None]:
        def handler(iface: object, proxy: object) -> None:
            def on_success(result: object) -> None:
                self._on_success(f"Game launch for {login}")
                self._set_panel_status("")
                card.set_running(int(result))  # type: ignore[arg-type]

            def on_error(err: object) -> None:
                self._on_error(str(err))
                self._set_panel_status("")
                card.set_launch_enabled(True)

            run_in_background(
                lambda on_progress: self._launch(
                    login,
                    cast(str | None, iface),
                    cast(str | None, proxy),
                    on_progress=on_progress,
                ),
                on_success=on_success,
                on_error=on_error,
                on_progress=self._set_panel_status,
                parent=self,
            )

        return handler

    def add_account(self, account: dict, all_interface: dict) -> None:
        card = self._append_card(account, all_interface)
        self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)

    def remove_account(self, login: str) -> None:
        for card in self._cards[:]:
            if card.login == login and not card.is_running:
                self._cards_layout.removeWidget(card)
                card.hide()
                card.deleteLater()
                self._cards.remove(card)

    def update_interfaces(self, all_interface: dict[str, tuple[str, str]]) -> None:
        for card in self._cards:
            card.update_interfaces(all_interface)

    @property
    def cards(self) -> list[AccountCard]:
        return self._cards


def make_unavailable_page(game_title: str) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label = BodyLabel(
        f"{game_title} client not found.\n"
        f"Install game via Ankama launcher then relaunch application."
    )
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {RED_HEXA};")
    layout.addWidget(label)
    return page
