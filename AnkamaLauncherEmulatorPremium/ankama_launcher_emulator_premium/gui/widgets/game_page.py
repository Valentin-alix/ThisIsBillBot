from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel

from ankama_launcher_emulator_premium.gui.consts import RED_HEXA
from ankama_launcher_emulator_premium.gui.utils import run_in_background
from ankama_launcher_emulator_premium.gui.widgets.account_card import AccountCard
from ankama_launcher_emulator_premium.gui.widgets.download_banner import DownloadBanner
from ankama_launcher_emulator_premium.interfaces.qt_types import (
    LaunchGameCallback,
    QtParent,
    StoredAccount,
    StoredAccounts,
)
from ankama_launcher_emulator_premium.utils.account_settings import (
    load_account_settings,
)


class GamePage(QWidget):
    """Scrollable list of AccountCards with a download progress banner."""

    def __init__(
        self,
        accounts: StoredAccounts,
        launch: LaunchGameCallback,
        on_success: Callable[[str], None],
        on_error: Callable[[str], None],
        parent: QtParent = None,
    ) -> None:
        super().__init__(parent)
        self._launch = launch
        self._on_success = on_success
        self._on_error = on_error
        self._cards: list[AccountCard] = []
        self._setup_ui(accounts)

    def _setup_ui(self, accounts: StoredAccounts) -> None:
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
            self._append_card(account, container)

        self._cards_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(self._banner)
        layout.addWidget(scroll, 1)

    def _append_card(
        self,
        account: StoredAccount,
        parent: QtParent = None,
    ) -> AccountCard:
        login = account.apikey.login
        acc_config = load_account_settings(login)
        card = AccountCard(
            login,
            parent,
            proxy_url=acc_config.proxy_url,
        )
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

    def _make_launch_handler(self, login: str, card: AccountCard) -> Callable[[object], None]:
        def handler(proxy: object) -> None:
            def task(on_progress: Callable[[str], None]) -> int:
                return self._launch(
                    login,
                    proxy if isinstance(proxy, str) else None,
                    on_progress,
                )

            def on_success(result: int) -> None:
                self._on_success(f"Game launch for {login}")
                self._set_panel_status("")
                card.set_running(result)

            def on_error(err: object) -> None:
                self._on_error(str(err))
                self._set_panel_status("")
                card.set_launch_enabled(True)

            run_in_background(
                task,
                on_success=on_success,
                on_error=on_error,
                on_progress=self._set_panel_status,
                parent=self,
            )

        return handler

    def add_account(self, account: StoredAccount) -> None:
        card = self._append_card(account)
        self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)

    def remove_account(self, login: str) -> None:
        for card in self._cards[:]:
            if card.login == login and not card.is_running:
                self._cards_layout.removeWidget(card)
                card.hide()
                card.deleteLater()
                self._cards.remove(card)

    @property
    def cards(self) -> list[AccountCard]:
        return self._cards


def make_unavailable_page(game_title: str) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label = BodyLabel(
        f"{game_title} client not found.\nInstall game via Ankama launcher then relaunch application."
    )
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    label.setStyleSheet(f"color: {RED_HEXA};")
    layout.addWidget(label)
    return page
