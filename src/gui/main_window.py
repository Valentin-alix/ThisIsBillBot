from functools import partial
from typing import Literal

from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfileController,
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QCloseEvent, QColor, QIcon
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import (
    FluentIcon,
    NavigationItemPosition,
    PrimaryPushButton,
    SplashScreen,
)
from qfluentwidgets.components.navigation import NavigationDisplayMode, NavigationWidget

from src import const
from src.const import LOGO_FILE
from src.controller.bot_config import BotConfigController
from src.core.bot.bot import Bot
from src.core.signals.log_signals import LogSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.gui.fragments.account_stacked_widget import AccountStackedWidget
from src.gui.fragments.app_fluent_window import AppFluentWindow
from src.gui.fragments.sidebar_item import SidebarItem
from src.services.logging_utils.loggers import init_root_gui_logging


class MainWindow(AppFluentWindow):
    account_widgets: list[AccountStackedWidget]
    bots_by_login: dict[str, Bot]

    def __init__(self, title: str, shared_signals: SharedSignals) -> None:
        super().__init__(parent=None)

        self.global_log_signals = LogSignals()
        if const.DEBUG:
            init_root_gui_logging(self.global_log_signals)

        self.title = title
        self.shared_signals = shared_signals
        self.setWindowTitle(self.title)
        self.resize(BASE_WIDTH, BASE_HEIGHT)
        self.setWindowIcon(QIcon(LOGO_FILE))
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

        self.disconnected_icon = FluentIcon.PEOPLE.icon(color=QColor(255, 0, 0))
        self.connected_icon = FluentIcon.PEOPLE.icon(color=QColor(0, 255, 0))

        self.account_widgets: list[AccountStackedWidget] = []
        self.bots_by_login: dict[str, Bot] = {}
        self._close_requested = False
        self._shutdown_finished = False
        self._init_sync_button()
        self.shared_signals.new_bot_added.connect(self.add_account)
        self.shared_signals.bot_removed.connect(self.remove_account)
        self.shared_signals.shutdown_finished.connect(self.complete_shutdown)

    def init_accounts(self, account_by_id: dict[int, Bot]) -> None:
        for account in account_by_id.values():
            self.add_account(account)

    def add_account(self, account: Bot) -> None:
        login = account.account.apikey.login
        self.bots_by_login[login] = account

        account_widget = AccountStackedWidget(self.global_log_signals, login, account)
        self.account_widgets.append(account_widget)
        navigation_widget = SidebarItem(
            account.bot_signals, self.disconnected_icon, login, True, parent=self
        )
        account_widget.setObjectName(login)
        self.addWidget(
            account_widget,
            navigation_widget,
            position=NavigationItemPosition.SCROLL,
        )
        self.navigationInterface.panel.expand()

        bot_config_controller = BotConfigController()
        config = bot_config_controller.get_bot_config(login)

        profiles = ScheduleProfileController().get_profile_display_names()
        selected_profile = config.schedule_profile
        navigation_widget.populate_schedule_profiles(profiles, selected_profile)
        navigation_widget.schedule_profile_changed.connect(
            partial(self._on_schedule_profile_changed, login)
        )

        selected_mode = config.connection_mode
        navigation_widget.populate_connection_mode(selected_mode)
        navigation_widget.connection_mode_changed.connect(
            partial(self._on_connection_mode_changed, login)
        )

        account.game_info_signals.character_name.connect(
            lambda name: navigation_widget.set_title(  # type: ignore
                f"{account.account.apikey.login.split('@')[0]} : {name}"
            )  # type: ignore
        )

        account.game_info_signals.in_fight.connect(navigation_widget.show_battle_icon)
        account.game_info_signals.is_ready_to_play.connect(
            lambda: navigation_widget.set_left_icon(self.connected_icon)
        )
        account.game_info_signals.disconnected.connect(
            lambda: navigation_widget.set_left_icon(self.disconnected_icon)
        )
        account.game_info_signals.disconnected.connect(
            lambda: navigation_widget.set_title(login)
        )

    def remove_account(self, account: Bot) -> None:
        login = account.account.apikey.login
        self.bots_by_login.pop(login, None)

        account_widget = next(
            (widget for widget in self.account_widgets if widget.objectName() == login),
            None,
        )
        if account_widget is None:
            return

        self.account_widgets.remove(account_widget)
        self.removeWidget(login, account_widget)
        account_widget.deleteLater()

        if self.account_widgets:
            self.switchTo(self.account_widgets[0])
            self.navigationInterface.setCurrentItem(
                self.account_widgets[0].objectName()
            )

    def _on_schedule_profile_changed(self, login: str, profile_id: str) -> None:
        selected_profile = profile_id or None
        bot_config_controller = BotConfigController()
        bot_config_controller.assign_profile(login, selected_profile)
        bot = self.bots_by_login[login]
        bot.scheduler.update_profile(selected_profile)

    def _on_connection_mode_changed(
        self, login: str, mode: Literal["mitm", "socket"]
    ) -> None:
        BotConfigController().assign_mode(login, mode)

    def _init_sync_button(self) -> None:
        def manage_visibility_sync_btn(display_mode: NavigationDisplayMode) -> None:
            if display_mode == NavigationDisplayMode.COMPACT:
                self.sync_widget.hide()
            else:
                self.sync_widget.show()

        class SyncButtonWidget(NavigationWidget):
            def __init__(self, parent: QWidget | None = None) -> None:
                super().__init__(isSelectable=False, parent=parent)
                layout = QHBoxLayout(self)
                layout.setContentsMargins(12, 0, 12, 0)
                self.button = PrimaryPushButton(
                    FluentIcon.SYNC, "Synchronisez les comptes"
                )
                layout.addWidget(self.button)

        self.sync_widget = SyncButtonWidget(self)
        self.sync_widget.button.clicked.connect(
            lambda: self.shared_signals.synchronize_bots.emit()
        )
        self.navigationInterface.displayModeChanged.connect(manage_visibility_sync_btn)

        self.navigationInterface.addWidget(
            routeKey="sync_button",
            widget=self.sync_widget,
            position=NavigationItemPosition.BOTTOM,
        )

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        if self._shutdown_finished:
            super().closeEvent(a0)
            return

        if a0 is not None:
            a0.ignore()
        if self._close_requested:
            return

        self._close_requested = True
        self.setEnabled(False)
        self.shared_signals.closed.emit()

    def complete_shutdown(self) -> None:
        self._shutdown_finished = True
        self.close()
