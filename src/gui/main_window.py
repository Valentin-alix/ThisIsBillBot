from functools import partial
from typing import Literal

from ankama_launcher_emulator_premium.utils.internet import (
    get_available_network_interfaces,
)
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QCloseEvent, QColor, QIcon
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
    NavigationItemPosition,
    PrimaryPushButton,
    SplashScreen,
    SwitchButton,
)
from qfluentwidgets.components.navigation import NavigationDisplayMode, NavigationWidget

from src import const
from src.const import LOGO_FILE
from src.controller.bot_config import BotConfig, BotConfigController
from src.controller.schedule_profile_controller import ScheduleProfileController
from src.core.bot.bot import Bot
from src.core.signals.global_log_signals import GlobalLogSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.gui.fragments.account_stacked_widget import AccountStackedWidget
from src.gui.fragments.app_fluent_window import AppFluentWindow
from src.gui.fragments.sidebar_item import SidebarItem
from src.services.logging.logger import init_gui_global_logging


class MainWindow(AppFluentWindow):
    account_widgets: list[AccountStackedWidget]
    bots_by_login: dict[str, Bot]

    def __init__(self, title: str, shared_signals: SharedSignals) -> None:
        super().__init__(parent=None)

        self.global_log_signals = GlobalLogSignals()
        init_gui_global_logging(self.global_log_signals)

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
        self._init_debug_button()
        self._init_sync_button()
        self.shared_signals.new_bot_added.connect(self.add_account)
        self.shared_signals.bot_removed.connect(self.remove_account)

    def init_accounts(self, account_by_id: dict[int, Bot]) -> None:
        for account in account_by_id.values():
            self.add_account(account)

    def add_account(self, account: Bot) -> None:
        login = account.account["apikey"]["login"]
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

        current_config = BotConfigController().get_bot_config_by_login().get(login)

        profiles = ScheduleProfileController().get_profile_display_names()
        selected_profile = current_config.schedule_profile if current_config else None
        navigation_widget.populate_schedule_profiles(profiles, selected_profile)
        navigation_widget.schedule_profile_changed.connect(
            partial(self._on_schedule_profile_changed, login)
        )

        interfaces = get_available_network_interfaces()
        selected_ip = current_config.network_interface if current_config else None
        navigation_widget.populate_network_interfaces(interfaces, selected_ip)
        navigation_widget.network_interface_changed.connect(
            partial(self._on_network_interface_changed, login)
        )

        selected_mode = current_config.connection_mode if current_config else "mitm"
        navigation_widget.populate_connection_mode(selected_mode)
        navigation_widget.connection_mode_changed.connect(
            partial(self._on_connection_mode_changed, login)
        )

        account.game_info_signals.character_name.connect(navigation_widget.set_title)

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
        login = account.account["apikey"]["login"]
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
        profile = profile_id if profile_id else None

        configs = BotConfigController().get_bot_config_by_login()
        existing_config = configs.get(login)
        if existing_config:
            updated_config = existing_config.model_copy(
                update={"schedule_profile": profile}
            )
        else:
            updated_config = BotConfig(schedule_profile=profile)
        BotConfigController().update_bot_config_by_login(updated_config, login)

        bot = self.bots_by_login.get(login)
        if bot:
            bot.scheduler.update_profile(profile)

    def _on_network_interface_changed(self, login: str, ip: str) -> None:
        configs = BotConfigController().get_bot_config_by_login()
        existing_config = configs.get(login)
        if existing_config:
            updated_config = existing_config.model_copy(
                update={"network_interface": ip if ip else None}
            )
        else:
            updated_config = BotConfig(network_interface=ip if ip else None)
        BotConfigController().update_bot_config_by_login(updated_config, login)

    def _on_connection_mode_changed(self, login: str, mode: str) -> None:
        typed_mode: Literal["mitm", "socket"] = "socket" if mode == "socket" else "mitm"
        configs = BotConfigController().get_bot_config_by_login()
        existing_config = configs.get(login)
        if existing_config:
            updated_config = existing_config.model_copy(
                update={"connection_mode": typed_mode}
            )
        else:
            updated_config = BotConfig(connection_mode=typed_mode)
        BotConfigController().update_bot_config_by_login(updated_config, login)

    def _init_debug_button(self) -> None:
        class DebugSwitchWidget(NavigationWidget):
            def __init__(self, parent: QWidget | None = None) -> None:
                super().__init__(isSelectable=False, parent=parent)
                self.setFixedHeight(48)
                layout = QHBoxLayout(self)
                layout.setContentsMargins(12, 8, 12, 8)

                icon_label = BodyLabel()
                icon_label.setPixmap(
                    FluentIcon.CODE.icon(color=QColor(255, 255, 255)).pixmap(16, 16)
                )
                layout.addWidget(icon_label)

                text_label = BodyLabel("Debug")
                layout.addWidget(text_label)

                layout.addStretch()

                self.switch = SwitchButton()
                self.switch.setChecked(const.DEBUG)
                layout.addWidget(self.switch, alignment=Qt.AlignmentFlag.AlignRight)

        self.debug_widget = DebugSwitchWidget(self)
        self.debug_widget.switch.checkedChanged.connect(self._on_debug_toggled)

        self.navigationInterface.addWidget(
            routeKey="debug_toggle",
            widget=self.debug_widget,
            position=NavigationItemPosition.BOTTOM,
        )

    def _on_debug_toggled(self, checked: bool) -> None:
        const.DEBUG = checked

        for account_widget in self.account_widgets:
            account_widget.set_debug_visibility(checked)

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
                self.button = PrimaryPushButton(FluentIcon.SYNC, "Sync")
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
        self.shared_signals.closed.emit()
        super().closeEvent(a0)
