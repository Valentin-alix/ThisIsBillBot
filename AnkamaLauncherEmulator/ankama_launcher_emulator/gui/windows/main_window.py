from typing import Callable, cast

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, InfoBar, InfoBarPosition, TitleLabel

from ankama_launcher_emulator.consts import (
    CYTRUS_INSTALLED,
    DOFUS_INSTALLED,
    RESOURCES,
    RETRO_INSTALLED,
    ZAAP_PATH,
)
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator.gui.consts import (
    DOFUS_3_TITLE,
    DOFUS_RETRO_TITLE,
    ORANGE_HEXA,
    RED_HEXA,
)
from ankama_launcher_emulator.gui.utils import run_in_background
from ankama_launcher_emulator.gui.widgets.game_page import (
    GamePage,
    make_unavailable_page,
)
from ankama_launcher_emulator.gui.widgets.game_selector_card import GameSelectorCard
from ankama_launcher_emulator.gui.widgets.star_bar import StarBar, has_shown_star_repo
from ankama_launcher_emulator.gui.widgets.unregistered_section import (
    UnregisteredSection,
)
from ankama_launcher_emulator.haapi.accounts import Account, load_unregistered_accounts
from ankama_launcher_emulator.haapi.browser_oauth_authenticator import authenticate
from ankama_launcher_emulator.server.server import AnkamaLauncherServer
from ankama_launcher_emulator.utils.internet import get_available_network_interfaces
from ankama_launcher_emulator.utils.proxy import build_proxy_listener


class MainWindow(QMainWindow):
    def __init__(
        self,
        server: AnkamaLauncherServer,
        accounts: list,
        all_interface: dict[str, tuple[str, str]],
    ):
        super().__init__()
        self._server = server
        self._accounts: list = accounts
        self._interfaces: dict[str, tuple[str, str]] = all_interface
        self._is_refreshing = False
        self._dofus_page: QWidget | None = None
        self._retro_page: QWidget | None = None
        self._unregistered_section: UnregisteredSection | None = None
        self._setup_ui(accounts, all_interface)
        self._start_refresh_timer()

    def _setup_ui(self, accounts: list, all_interface: dict) -> None:
        self.setWindowTitle("Ankama Launcher")
        self.setMinimumWidth(1000)
        self.resize(1150, 600)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        if not has_shown_star_repo():
            layout.addWidget(StarBar())

        unregistered = load_unregistered_accounts(accounts)

        if not accounts and not unregistered:
            label = BodyLabel(
                f"No account found.\n"
                f"Check that ankama launcher is installed et have logged account.\n"
                f"Expected path : {ZAAP_PATH}/keydata/"
            )
            label.setStyleSheet(f"color: {RED_HEXA};")
            label.setWordWrap(True)
            layout.addWidget(label)
            return

        if unregistered:
            self._unregistered_section = UnregisteredSection(
                unregistered,
                all_interface,
                authenticate,
                on_success=self._show_success,
                on_error=self._show_error,
            )
            layout.addWidget(self._unregistered_section)

        if accounts:
            self._setup_game_section(layout, accounts, all_interface)

    def _setup_game_section(
        self, layout: QVBoxLayout, accounts: list, all_interface: dict
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
        self._retro_selector.clicked.connect(
            lambda: self._select_game(is_dofus_3=False)
        )

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
                all_interface,
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
                all_interface,
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
        self._stack.setCurrentWidget(
            self._dofus_page if is_dofus_3 else self._retro_page
        )

    def _launch_dofus(
        self,
        login: str,
        interface_ip: str | None,
        proxy_url: str | None,
        on_progress: Callable[[str], None] | None = None,
    ) -> int:
        proxy_listener, proxy_url = build_proxy_listener(proxy_url)
        return self._server.launch_dofus(
            login,
            proxy_listener=proxy_listener,
            proxy_url=proxy_url,
            interface_ip=interface_ip,
            on_progress=on_progress,
        )

    def _launch_retro(
        self,
        login: str,
        interface_ip: str | None,
        proxy_url: str | None,
        on_progress: Callable[[str], None] | None = None,
    ) -> int:
        return self._server.launch_retro(
            login,
            proxy_url=proxy_url,
            interface_ip=interface_ip,
            on_progress=on_progress,
        )

    def _show_success(self, msg: str) -> None:
        InfoBar.success(
            "", msg, duration=3000, position=InfoBarPosition.TOP_RIGHT, parent=self
        )

    def _show_error(self, msg: str) -> None:
        InfoBar.error(
            "", msg, duration=6000, position=InfoBarPosition.TOP_RIGHT, parent=self
        )

    def _start_refresh_timer(self) -> None:
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(10_000)
        self._refresh_timer.timeout.connect(self._schedule_refresh)
        self._refresh_timer.start()

    def _schedule_refresh(self) -> None:
        if self._is_refreshing:
            return
        self._is_refreshing = True

        def fetch(_on_progress: Callable) -> tuple:
            stored = CryptoHelper.getStoredApiKeys()
            interfaces = get_available_network_interfaces()
            unregistered = load_unregistered_accounts(stored)
            return stored, interfaces, unregistered

        def on_success(result: object) -> None:
            stored, interfaces, unregistered = cast(tuple, result)
            self._apply_refresh(stored, interfaces, unregistered)

        run_in_background(
            fetch,
            on_success=on_success,
            on_error=lambda _: setattr(self, "_is_refreshing", False),
            parent=self,
        )

    def _apply_refresh(
        self,
        new_accounts: list,
        new_interfaces: dict[str, tuple[str, str]],
        new_unregistered: list[Account],
    ) -> None:
        self._is_refreshing = False

        current_logins: set[str] = {acc["apikey"]["login"] for acc in self._accounts}
        new_logins: set[str] = {acc["apikey"]["login"] for acc in new_accounts}

        if current_logins != new_logins:
            if not self._accounts and new_accounts:
                self._accounts = new_accounts
                self._interfaces = new_interfaces
                self._setup_ui(new_accounts, new_interfaces)
                return

            for account in new_accounts:
                login = account["apikey"]["login"]
                if login in current_logins:
                    continue
                if isinstance(self._dofus_page, GamePage):
                    self._dofus_page.add_account(account, new_interfaces)
                if isinstance(self._retro_page, GamePage):
                    self._retro_page.add_account(account, new_interfaces)

            for login in current_logins - new_logins:
                if isinstance(self._dofus_page, GamePage):
                    self._dofus_page.remove_account(login)
                if isinstance(self._retro_page, GamePage):
                    self._retro_page.remove_account(login)

            self._accounts = new_accounts

        if new_interfaces != self._interfaces:
            if isinstance(self._dofus_page, GamePage):
                self._dofus_page.update_interfaces(new_interfaces)
            if isinstance(self._retro_page, GamePage):
                self._retro_page.update_interfaces(new_interfaces)
            if self._unregistered_section is not None:
                self._unregistered_section.update_interfaces(new_interfaces)
            self._interfaces = new_interfaces

        if self._unregistered_section is not None:
            self._unregistered_section.refresh(new_unregistered, new_interfaces)
