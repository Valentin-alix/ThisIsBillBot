import json
from datetime import datetime
from functools import partial

from PyQt6.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    FluentIcon,
    LineEdit,
    PrimaryPushButton,
    SegmentedWidget,
)

from src.core.bot.bot import Bot
from src.core.signals.global_log_signals import GlobalLogSignals
from src.gui.pages.debugs.listeners_stats import ListenersStatsWidget
from src.gui.pages.debugs.logs import LogsWidget
from src.gui.pages.debugs.message_detail import MessageDetailWidget
from src.gui.pages.debugs.message_table import MessageTable
from src.gui.utils.profiling import profiled_slot
from src.protocol.message import MessageInfo


def _require_message_info(value: object) -> MessageInfo:
    if not isinstance(value, MessageInfo):
        raise TypeError("Expected a MessageInfo payload in the message table model")
    return value


def _parse_sub_msg_name(sub_msg_name: str) -> tuple[str | None, str]:
    """Returns (obf_type, decoded_type). obf_type is None for connection messages."""
    if " -> " in sub_msg_name:
        obf, decoded = sub_msg_name.split(" -> ", 1)
        return obf, decoded
    return None, sub_msg_name


class SnifferWidget(QWidget):
    msg_table: MessageTable
    msg_detail: MessageDetailWidget
    play_btn: PrimaryPushButton
    stop_btn: PrimaryPushButton

    def __init__(
        self,
        bot: Bot,
        global_log_signals: GlobalLogSignals,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.bot = bot
        self.global_log_signals = global_log_signals
        self.is_playing: bool = True
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 4, 4, 4)
        self.v_layout.setSpacing(0)
        self.setLayout(self.v_layout)
        self.init_top_content()
        self.init_content()
        self.bot.msg_info_signals.msg_info.connect(
            profiled_slot(self.on_receive_msg_info)
        )

    def init_top_content(self) -> None:
        top_content = QWidget(self)
        # prevent top header from expanding in height
        top_content.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self.v_layout.addWidget(top_content)
        top_content_layout = QHBoxLayout()
        top_content.setLayout(top_content_layout)
        top_content_layout.setContentsMargins(0, 0, 0, 0)
        reset_btn = PrimaryPushButton(FluentIcon.DELETE, "Réinitialiser", top_content)
        reset_btn.clicked.connect(self.on_reset)
        top_content_layout.addWidget(reset_btn)

        self.play_btn = PrimaryPushButton(
            FluentIcon.PLAY, "Lancer le sniffer", top_content
        )
        if self.is_playing:
            self.play_btn.hide()
        self.play_btn.clicked.connect(self.on_play)
        top_content_layout.addWidget(self.play_btn)

        self.stop_btn = PrimaryPushButton(
            FluentIcon.PAUSE, "Arrêter le sniffer", top_content
        )
        if not self.is_playing:
            self.stop_btn.hide()
        self.stop_btn.clicked.connect(self.on_stop)
        top_content_layout.addWidget(self.stop_btn)

        export_btn = PrimaryPushButton(
            FluentIcon.SAVE, "Exporter les messages", top_content
        )
        export_btn.clicked.connect(self.on_export_messages)
        top_content_layout.addWidget(export_btn)

    def init_content(self) -> None:
        content = QWidget(self)
        content_layout = QHBoxLayout()
        content.setLayout(content_layout)
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # left side: filter + message table
        self.msg_table = MessageTable(parent=self)
        self.msg_table.table.clicked.connect(self.on_click_msg)

        left_widget = QWidget(self)
        left_widget_layout = QVBoxLayout()
        left_widget.setLayout(left_widget_layout)
        left_widget_layout.setContentsMargins(0, 0, 0, 0)
        left_widget_layout.setSpacing(0)

        wrapper_filter = QWidget(left_widget)
        wrapper_filter_layout = QHBoxLayout()
        wrapper_filter.setLayout(wrapper_filter_layout)
        # filter bar should not expand vertically
        wrapper_filter.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        wrapper_filter_layout.setContentsMargins(0, 16, 0, 0)
        custom_filter = LineEdit(wrapper_filter)
        wrapper_filter_layout.addWidget(custom_filter)
        custom_filter.setPlaceholderText("Contenu")
        custom_filter.textChanged.connect(
            partial(self.msg_table.table.header.on_new_filter_input, 4)
        )

        left_widget_layout.addWidget(wrapper_filter)
        left_widget_layout.addWidget(self.msg_table)
        left_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.msg_table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # right side: message detail and logs/listeners tabs
        self.msg_detail = MessageDetailWidget(parent=self)
        self.msg_detail.hide()
        self.msg_detail.quit_btn.clicked.connect(self.on_close_detail)

        self.right_splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.right_splitter.addWidget(self.msg_detail)

        if self.bot.log_signals is not None:
            debug_tabs_widget = QWidget(self)
            debug_tabs_widget_layout = QVBoxLayout()
            debug_tabs_widget.setLayout(debug_tabs_widget_layout)
            debug_tabs_widget_layout.setContentsMargins(0, 16, 0, 0)
            debug_tabs_widget_layout.setSpacing(0)

            debug_pivot = SegmentedWidget(debug_tabs_widget)
            debug_tabs_widget_layout.addWidget(debug_pivot)

            debug_stacked = QStackedWidget(debug_tabs_widget)
            debug_tabs_widget_layout.addWidget(debug_stacked)

            logs_widget = LogsWidget(
                global_signals=self.global_log_signals,
                log_signals=self.bot.log_signals,
                parent=debug_stacked,
            )
            debug_stacked.addWidget(logs_widget)

            listeners_widget = ListenersStatsWidget(
                event_manager=self.bot.event_manager, parent=debug_stacked
            )
            debug_stacked.addWidget(listeners_widget)

            debug_pivot.addItem(
                routeKey="logs",
                text="Logs",
                onClick=lambda: debug_stacked.setCurrentWidget(logs_widget),
            )
            debug_pivot.addItem(
                routeKey="listeners",
                text="Listeners",
                onClick=lambda: self._show_listeners_tab(
                    debug_stacked, listeners_widget
                ),
            )
            debug_pivot.setCurrentItem("logs")

            self.right_splitter.addWidget(debug_tabs_widget)

            self.logs_widget = logs_widget
            self.listeners_widget = listeners_widget
        else:
            self.logs_widget = None
            self.listeners_widget = None

        # main horizontal splitter: left (filter+table) | right (detail+logs)
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.right_splitter)
        # equal stretch: each side takes ~50% by default
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        # enforce initial equal proportions (pixels) so it appears 50/50
        splitter.setSizes([800, 800])

        # right vertical splitter equal split when both widgets present
        if self.logs_widget is not None:
            self.right_splitter.setStretchFactor(0, 2)
            self.right_splitter.setStretchFactor(1, 1)
            # enforce equal vertical split when both present
            self.right_splitter.setSizes([300, 150])

        content_layout.addWidget(splitter)
        self.v_layout.addWidget(content)

        self.v_layout.setStretch(2, 1)

    @pyqtSlot(MessageInfo, bool)
    def on_receive_msg_info(
        self, msg_info: MessageInfo, was_send_from_proxy: bool
    ) -> None:
        if self.is_playing:
            self.msg_table.add_row(msg_info, was_send_from_proxy)

    @pyqtSlot()
    def on_play(self) -> None:
        self.is_playing = True
        self.play_btn.hide()
        self.stop_btn.show()

    @pyqtSlot()
    def on_stop(self) -> None:
        self.is_playing = False
        self.stop_btn.hide()
        self.play_btn.show()

    @pyqtSlot()
    def on_export_messages(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"sniffer_{timestamp}.json"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les messages", default_filename, "Fichiers JSON (*.json)"
        )
        if not file_path:
            return

        model = self.msg_table.table.item_model
        entries: list[dict[str, object]] = []

        for row in range(model.rowCount()):
            msg_info = _require_message_info(
                model.data(model.index(row, 4), Qt.ItemDataRole.UserRole)
            )
            obf_type, decoded_type = _parse_sub_msg_name(msg_info.sub_msg_name)
            entries.append(
                {
                    "heure": msg_info.received_time.strftime("%H:%M:%S"),
                    "origine": "Serveur" if msg_info.from_server else "Client",
                    "type_non_obfusque": decoded_type,
                    "type_obfusque": obf_type,
                    "contenu_obfusque": msg_info.obf_msg_json,
                    "contenu_non_obfusque": msg_info.msg_json,
                }
            )

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(entries, file, ensure_ascii=False, indent=2)

    @pyqtSlot()
    def on_reset(self) -> None:
        self.msg_table.table.item_model.remove_rows(
            0, len(self.msg_table.table.item_model._data)
        )
        if self.logs_widget:
            self.logs_widget.logs_table.table.item_model.remove_rows(
                0, len(self.logs_widget.logs_table.table.item_model._data)
            )

    @pyqtSlot(QModelIndex)
    def on_click_msg(self, model_index: QModelIndex) -> None:
        source_index = self.msg_table.table.proxy_model.mapToSource(model_index)
        model = self.msg_table.table.item_model
        msg_infos = _require_message_info(
            model.data(model.index(source_index.row(), 4), Qt.ItemDataRole.UserRole)
        )
        self.msg_detail.set_content(msg_infos.msg_json, msg_infos.obf_msg_json)
        self.msg_detail.show()

    @pyqtSlot()
    def on_close_detail(self) -> None:
        self.msg_detail.hide()

    def _show_listeners_tab(
        self,
        debug_stacked: QStackedWidget,
        listeners_widget: ListenersStatsWidget,
    ) -> None:
        debug_stacked.setCurrentWidget(listeners_widget)
        listeners_widget.init()
