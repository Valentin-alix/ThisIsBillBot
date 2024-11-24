import asyncio
from typing import Callable, cast

from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel

from ankama_launcher_emulator.gui.consts import ORANGE_HEXA
from ankama_launcher_emulator.gui.utils import run_in_background
from ankama_launcher_emulator.gui.widgets.unregistered_account_card import (
    UnregisteredAccountCard,
)
from ankama_launcher_emulator.haapi.accounts import Account
from ankama_launcher_emulator.utils.account_settings import load_account_settings


class UnregisteredSection(QWidget):
    """Panel listing accounts that still need to be authenticated."""

    def __init__(
        self,
        accounts: list[Account],
        all_interface: dict[str, tuple[str, str]],
        authenticate: Callable,  # async: authenticate(email, password, interface_ip, proxy_url)
        on_success: Callable[[str], None],
        on_error: Callable[[str], None],
        parent=None,
    ):
        super().__init__(parent)
        self._authenticate = authenticate
        self._on_success = on_success
        self._on_error = on_error
        self.cards: list[UnregisteredAccountCard] = []
        self._setup_ui(accounts, all_interface)

    def _setup_ui(self, accounts: list[Account], all_interface: dict) -> None:
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)

        header = BodyLabel("Accounts to authenticate")
        header.setStyleSheet(f"color: {ORANGE_HEXA};")
        self._layout.addWidget(header)

        for acc in accounts:
            card = self._make_card(acc, all_interface)
            self.cards.append(card)
            self._layout.addWidget(card)

    def _make_card(self, acc: Account, all_interface: dict) -> UnregisteredAccountCard:
        saved_ip, saved_proxy = load_account_settings(acc["email"])
        card = UnregisteredAccountCard(
            acc["email"],
            acc["password"],
            all_interface,
            interface_ip=saved_ip,
            proxy_url=saved_proxy,
        )
        card.authenticate_requested.connect(
            self._make_auth_handler(acc["email"], acc["password"], card)
        )
        return card

    def _make_auth_handler(
        self, email: str, password: str, card: UnregisteredAccountCard
    ) -> Callable:
        def handler(iface: object, proxy: object) -> None:
            def task(_on_progress: Callable) -> None:
                asyncio.run(
                    self._authenticate(
                        email,
                        password,
                        interface_ip=cast(str | None, iface),
                        proxy_url=cast(str | None, proxy),
                    )
                )

            def on_success(_result: object) -> None:
                card.set_authenticating(False)
                self._on_success(f"Account {email} authenticated!")

            def on_error(err: object) -> None:
                card.set_authenticating(False)
                self._on_error(str(err))

            run_in_background(
                task, on_success=on_success, on_error=on_error, parent=self
            )

        return handler

    def refresh(self, new_unregistered: list[Account], interfaces: dict) -> None:
        current_emails = {card.email for card in self.cards}
        new_emails = {acc["email"] for acc in new_unregistered}
        if current_emails == new_emails:
            return
        new_by_email = {acc["email"]: acc for acc in new_unregistered}
        for card in self.cards[:]:
            if card.email not in new_emails:
                self._layout.removeWidget(card)
                card.hide()
                card.deleteLater()
                self.cards.remove(card)
        for email, acc in new_by_email.items():
            if email not in current_emails:
                card = self._make_card(acc, interfaces)
                self.cards.append(card)
                self._layout.addWidget(card)
        self.setVisible(bool(self.cards))

    def update_interfaces(self, all_interface: dict[str, tuple[str, str]]) -> None:
        for card in self.cards:
            card.update_interfaces(all_interface)
