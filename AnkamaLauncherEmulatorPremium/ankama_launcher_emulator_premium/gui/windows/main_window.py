from collections.abc import Callable

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, InfoBar, InfoBarPosition, TitleLabel

from ankama_launcher_emulator_premium.consts import (
    CYTRUS_INSTALLED,
    RESOURCES,
)
from ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator_premium.gui.consts import (
    DOFUS_3_TITLE,
    DOFUS_RETRO_TITLE,
    ORANGE_HEXA,
    RED_HEXA,
)
from ankama_launcher_emulator_premium.gui.utils import run_in_background
from ankama_launcher_emulator_premium.gui.widgets.game_page import (
    GamePage,
    make_unavailable_page,
)
from ankama_launcher_emulator_premium.gui.widgets.game_selector_card import (
    GameSelectorCard,
)
from ankama_launcher_emulator_premium.interfaces.qt_types import (
    ProgressCallback,
    StoredAccounts,
)
from ankama_launcher_emulator_premium.server.server import AnkamaLauncherServer
from ankama_launcher_emulator_premium.utils.environment import (
    DOFUS_INSTALLED,
    RETRO_INSTALLED,
    ZAAP_PATH,
)
from ankama_launcher_emulator_premium.utils.proxy import build_proxy_listener


class MainWindow(QMainWindow):
    def __init__(
        self,
        server: AnkamaLauncherServer,
        accounts: StoredAccounts,
    ) -> None:
        super().__init__()
        self._server = server
        self._accounts: StoredAccounts = accounts
        self._is_refreshing = False
        self._dofus_page: QWidget | None = None
        self._retro_page: QWidget | None = None
        self._setup_ui(accounts)
        self._start_refresh_timer()

    def _setup_ui(self, accounts: StoredAccounts) -> None:
        self.setWindowTitle("Ankama Launcher")
        self.setMinimumWidth(1000)
        self.resize(1150, 600)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        if not accounts:
            label = BodyLabel(
                f"No account found.\n"
                f"Check that ankama launcher is installed et have logged account.\n"
                f"Expected path : {ZAAP_PATH}/keydata/"
            )
            label.setStyleSheet(f"color: {RED_HEXA};")
            label.setWordWrap(True)
            layout.addWidget(label)
            return

        self._setup_game_section(layout, accounts)

    def _setup_game_section(
        self,
        layout: QVBoxLayout,
        accounts: StoredAccounts,
    ) -> None:
        self._dofus_selector = GameSelectorCard(
            DOFUS_3_TITLE, RESOURCES / "Dofus3.png", False, available=DOFUS_INSTALLED
        )
        self._retro_selector = GameSelectorCard(
            DOFUS_RETRO_TITLE,
            RESOURCES / "DofusRetro.png",
            False,
            available=RETRO_INSTALLED,
        )
        self._dofus_selector.clicked.connect(lambda: self._select_game(is_dofus_3=True))
        self._retro_selector.clicked.connect(lambda: self._select_game(is_dofus_3=False))

        selector_row = QHBoxLayout()
        selector_row.setSpacing(12)
        selector_row.addWidget(self._dofus_selector)
        selector_row.addWidget(self._retro_selector)
        layout.addLayout(selector_row)

        if not CYTRUS_INSTALLED:
            cytrus_warning = BodyLabel(
                "cytrus-v6 is not installed. Auto-update will not work.\n"
                "Install it with: npm install -g cytrus-v6"
            )
            cytrus_warning.setStyleSheet(f"color: {ORANGE_HEXA};")
            cytrus_warning.setWordWrap(True)
            layout.addWidget(cytrus_warning)

        self._title_label = TitleLabel(DOFUS_3_TITLE)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._title_label)

        self._stack = QStackedWidget()
        self._dofus_page = (
            GamePage(
                accounts,
                self._launch_dofus,
                on_success=self._show_success,
                on_error=self._show_error,
            )
            if DOFUS_INSTALLED
            else make_unavailable_page(DOFUS_3_TITLE)
        )
        self._retro_page = (
            GamePage(
                accounts,
                self._launch_retro,
                on_success=self._show_success,
                on_error=self._show_error,
            )
            if RETRO_INSTALLED
            else make_unavailable_page(DOFUS_RETRO_TITLE)
        )
        self._stack.addWidget(self._dofus_page)
        self._stack.addWidget(self._retro_page)
        layout.addWidget(self._stack)

        self._select_game(DOFUS_INSTALLED or not RETRO_INSTALLED)

    def _select_game(self, is_dofus_3: bool) -> None:
        self._title_label.setText(DOFUS_3_TITLE if is_dofus_3 else DOFUS_RETRO_TITLE)
        self._dofus_selector.set_active(is_dofus_3)
        self._retro_selector.set_active(not is_dofus_3)
        self._stack.setCurrentWidget(self._dofus_page if is_dofus_3 else self._retro_page)

    def _launch_dofus(
        self,
        login: str,
        proxy_url: str | None,
        on_progress: Callable[[str], None] | None = None,
    ) -> int:
        proxy_listener, proxy_url = build_proxy_listener(proxy_url)
        return self._server.launch_dofus(
            login,
            proxy_listener=proxy_listener,
            proxy_url=proxy_url,
            on_progress=on_progress,
        )

    def _launch_retro(
        self,
        login: str,
        proxy_url: str | None,
        on_progress: Callable[[str], None] | None = None,
    ) -> int:
        return self._server.launch_retro(
            login,
            proxy_url=proxy_url,
            on_progress=on_progress,
        )

    def _show_success(self, msg: str) -> None:
        InfoBar.success("", msg, duration=3000, position=InfoBarPosition.TOP_RIGHT, parent=self)

    def _show_error(self, msg: str) -> None:
        InfoBar.error("", msg, duration=6000, position=InfoBarPosition.TOP_RIGHT, parent=self)

    def _start_refresh_timer(self) -> None:
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(10_000)
        self._refresh_timer.timeout.connect(self._schedule_refresh)
        self._refresh_timer.start()

    def _schedule_refresh(self) -> None:
        if self._is_refreshing:
            return
        self._is_refreshing = True

        def fetch(
            _on_progress: ProgressCallback,
        ) -> StoredAccounts:
            stored = CryptoHelper.getStoredApiKeys()
            return stored

        def on_success(stored: StoredAccounts) -> None:
            self._apply_refresh(stored)

        run_in_background(
            fetch,
            on_success=on_success,
            on_error=lambda _: setattr(self, "_is_refreshing", False),
            parent=self,
        )

    def _apply_refresh(
        self,
        new_accounts: StoredAccounts,
    ) -> None:
        self._is_refreshing = False

        current_logins: set[str] = {acc.apikey.login for acc in self._accounts}
        new_logins: set[str] = {acc.apikey.login for acc in new_accounts}

        if current_logins != new_logins:
            if not self._accounts and new_accounts:
                self._accounts = new_accounts
                self._setup_ui(new_accounts)
                return

            for account in new_accounts:
                login = account.apikey.login
                if login in current_logins:
                    continue
                if isinstance(self._dofus_page, GamePage):
                    self._dofus_page.add_account(account)
                if isinstance(self._retro_page, GamePage):
                    self._retro_page.add_account(account)

            for login in current_logins - new_logins:
                if isinstance(self._dofus_page, GamePage):
                    self._dofus_page.remove_account(login)
                if isinstance(self._retro_page, GamePage):
                    self._retro_page.remove_account(login)

            self._accounts = new_accounts
