import logging
from functools import partial
from typing import Literal

from PyQt6.QtCore import QSize, QUrl
from PyQt6.QtGui import QCloseEvent, QColor, QIcon, QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import (
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    NavigationItemPosition,
    PrimaryPushButton,
    SplashScreen,
)
from qfluentwidgets.components.navigation import NavigationDisplayMode, NavigationWidget

from src import consts
from src.consts import LOGO_FILE
from src.controller.bot_config import BotConfigService
from src.core.bot.bot import Bot
from src.core.signals.log_signals import LogSignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.gui.fragments.account_stacked_widget import AccountStackedWidget
from src.gui.fragments.app_fluent_window import AppFluentWindow
from src.gui.fragments.sidebar_item import SidebarItem
from src.services.background import run_in_background
from src.services.hotreload.reloader import ReloadReport, reload_core_modules
from src.services.logging_utils.loggers import init_root_gui_logging

logger = logging.getLogger()
_BREED_ICON_URL_TEMPLATE = "https://api.dofusdb.fr/img/breeds/symbol_{breed_id}.png"


class MainWindow(AppFluentWindow):
    account_widgets: list[AccountStackedWidget]
    bots_by_login: dict[str, Bot]

    def __init__(self, title: str, shared_signals: SharedSignals) -> None:
        super().__init__(parent=None)

        self.global_log_signals = LogSignals()
        if consts.DEBUG:
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
        self._breed_icon_network_manager = QNetworkAccessManager(self)
        self._breed_icon_by_id: dict[int, QIcon] = {}

        self.account_widgets: list[AccountStackedWidget] = []
        self.bots_by_login: dict[str, Bot] = {}
        self._close_requested = False
        self._shutdown_finished = False
        self._init_reload_button()
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
        navigation_widget = SidebarItem(account.bot_signals, self.disconnected_icon, login, True, parent=self)
        navigation_widget.set_playing(account.is_playing_event.is_set())
        is_connected = account.is_connected_event.is_set()
        navigation_widget.set_connected(is_connected)
        if is_connected:
            navigation_widget.set_left_icon(self.connected_icon)
        account_widget.setObjectName(login)
        self.addWidget(
            account_widget,
            navigation_widget,
            position=NavigationItemPosition.SCROLL,
        )
        self.navigationInterface.panel.expand()

        bot_config_controller = BotConfigService()
        config = bot_config_controller.get_bot_config(login)

        selected_mode = config.connection_mode
        navigation_widget.populate_connection_mode(selected_mode)

        def on_connection_mode_changed(mode: str) -> None:
            assert mode in ("mitm", "socket"), f"Unknown connection mode {mode}"
            self._on_connection_mode_changed(login, mode)

        navigation_widget.connection_mode_changed.connect(on_connection_mode_changed)
        navigation_widget.disconnect_clicked.connect(lambda: self._on_disconnect_clicked(login))

        def on_connected(_characters: object) -> None:
            navigation_widget.set_left_icon(self.connected_icon)
            navigation_widget.set_connected(True)

        account.game_info_signals.connected.connect(on_connected)
        account.game_info_signals.character_name.connect(
            lambda name: navigation_widget.set_title(  # type: ignore
                f"{account.account.apikey.login.split('@')[0]} : {name}"
            )  # type: ignore
        )

        account.game_info_signals.in_fight.connect(navigation_widget.show_battle_icon)
        account.game_info_signals.is_ready_to_play.connect(
            partial(self._show_breed_icon, navigation_widget, account)
        )
        account.game_info_signals.disconnected.connect(
            lambda: navigation_widget.set_left_icon(self.disconnected_icon)
        )
        account.game_info_signals.disconnected.connect(lambda: navigation_widget.set_connected(False))
        account.game_info_signals.disconnected.connect(lambda: navigation_widget.set_title(login))

        if account.is_ready_to_play_event.is_set():
            self._show_breed_icon(navigation_widget, account)

    def _show_breed_icon(self, navigation_widget: SidebarItem, account: Bot) -> None:
        navigation_widget.set_left_icon(self.connected_icon)
        breed_id = account.game_state.fight.breed_id
        if breed_id <= 0:
            return

        cached_icon = self._breed_icon_by_id.get(breed_id)
        if cached_icon is not None:
            navigation_widget.set_left_icon(cached_icon)
            return

        request = QNetworkRequest(QUrl(_BREED_ICON_URL_TEMPLATE.format(breed_id=breed_id)))
        request.setTransferTimeout(10_000)
        reply = self._breed_icon_network_manager.get(request)
        if not reply:
            return
        reply.finished.connect(
            partial(
                self._on_breed_icon_reply_finished,
                reply,
                navigation_widget,
                account,
                breed_id,
            )
        )

    def _on_breed_icon_reply_finished(
        self,
        reply: QNetworkReply,
        navigation_widget: SidebarItem,
        account: Bot,
        breed_id: int,
    ) -> None:
        if reply.error() != QNetworkReply.NetworkError.NoError:
            logger.warning(
                "Cannot load breed icon %s for %s: %s",
                breed_id,
                account.account.apikey.login,
                reply.errorString(),
            )
            reply.deleteLater()
            return

        pixmap = QPixmap()
        if not pixmap.loadFromData(reply.readAll().data(), "PNG"):
            logger.warning(
                "Cannot load breed icon %s for %s: invalid PNG response",
                breed_id,
                account.account.apikey.login,
            )
            reply.deleteLater()
            return

        reply.deleteLater()
        breed_icon = QIcon(pixmap)
        self._breed_icon_by_id[breed_id] = breed_icon

        login = account.account.apikey.login
        if self.bots_by_login.get(login) is not account:
            return
        if not account.is_connected_event.is_set():
            return
        if account.game_state.fight.breed_id != breed_id:
            return
        navigation_widget.set_left_icon(breed_icon)

    def remove_account(self, account: Bot) -> None:
        login = account.account.apikey.login
        self.bots_by_login.pop(login, None)
        self._disconnect_game_info_signals(account)

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
            self.navigationInterface.setCurrentItem(self.account_widgets[0].objectName())

    def _disconnect_game_info_signals(self, account: Bot) -> None:
        for signal in (
            account.game_info_signals.connected,
            account.game_info_signals.character_name,
            account.game_info_signals.in_fight,
            account.game_info_signals.is_ready_to_play,
            account.game_info_signals.disconnected,
        ):
            try:
                signal.disconnect()
            except TypeError:
                pass

    def _on_connection_mode_changed(self, login: str, mode: Literal["mitm", "socket"]) -> None:
        BotConfigService().assign_mode(login, mode)

    def _on_disconnect_clicked(self, login: str) -> None:
        bot = self.bots_by_login[login]
        if not bot.is_connected_event.is_set():
            return
        bot.scheduler.disconnect_now()

    def _init_reload_button(self) -> None:
        def manage_visibility_reload_btn(display_mode: NavigationDisplayMode) -> None:
            if display_mode == NavigationDisplayMode.COMPACT:
                self.reload_widget.hide()
            else:
                self.reload_widget.show()

        class ReloadButtonWidget(NavigationWidget):
            def __init__(self, parent: QWidget | None = None) -> None:
                super().__init__(isSelectable=False, parent=parent)
                layout = QHBoxLayout(self)
                layout.setContentsMargins(12, 0, 12, 0)
                self.button = PrimaryPushButton(FluentIcon.UPDATE, "Recharger le code")
                layout.addWidget(self.button)

        self.reload_widget = ReloadButtonWidget(self)
        self.reload_widget.button.clicked.connect(self._on_reload_code_clicked)
        self.navigationInterface.displayModeChanged.connect(manage_visibility_reload_btn)

        self.navigationInterface.addWidget(
            routeKey="reload_button",
            widget=self.reload_widget,
            position=NavigationItemPosition.BOTTOM,
        )

    def _on_reload_code_clicked(self) -> None:
        self.reload_widget.button.setEnabled(False)
        run_in_background(
            lambda _progress: reload_core_modules(),
            on_success=self._on_reload_finished,
            on_error=self._on_reload_error,
        )

    def _on_reload_finished(self, report: ReloadReport) -> None:
        self.reload_widget.button.setEnabled(True)
        if report.errors:
            content = "\n".join(f"{name}: {error}" for name, error in report.errors.items())
            InfoBar.error(
                title="Erreur de rechargement",
                content=content,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=8000,
                parent=self,
            )
            return
        if not report.reloaded_modules:
            InfoBar.success(
                title="Rechargement du code",
                content="Aucun module modifié.",
                position=InfoBarPosition.BOTTOM_RIGHT,
                parent=self,
            )
            return
        InfoBar.success(
            title="Rechargement du code",
            content=(
                f"{len(report.reloaded_modules)} module(s) rechargé(s), "
                f"{report.patched_instance_count} instance(s) mise(s) à jour."
            ),
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=5000,
            parent=self,
        )

    def _on_reload_error(self, error: object) -> None:
        self.reload_widget.button.setEnabled(True)
        InfoBar.error(
            title="Erreur de rechargement",
            content=str(error),
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=8000,
            parent=self,
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
