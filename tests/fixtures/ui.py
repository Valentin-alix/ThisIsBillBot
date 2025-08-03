from dataclasses import dataclass, field
from unittest.mock import MagicMock, Mock


@dataclass
class NavigationInterfaceFake:
    setCurrentItem: Mock = field(default_factory=Mock)


@dataclass
class AccountWidgetFake:
    login: str
    deleteLater: Mock = field(default_factory=Mock)

    def objectName(self) -> str:
        return self.login


@dataclass
class MainWindowShellFake:
    bots_by_login: dict[str, Mock]
    account_widgets: list[AccountWidgetFake]
    removeWidget: Mock = field(default_factory=Mock)
    switchTo: Mock = field(default_factory=Mock)
    navigationInterface: NavigationInterfaceFake = field(default_factory=NavigationInterfaceFake)


def make_main_window_shell(*logins: str) -> MainWindowShellFake:
    widgets = [AccountWidgetFake(login) for login in logins]
    return MainWindowShellFake(
        bots_by_login={login: MagicMock() for login in logins},
        account_widgets=widgets,
    )
