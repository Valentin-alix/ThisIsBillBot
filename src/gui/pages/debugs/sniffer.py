from functools import partial
from typing import cast

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
    PivotItem,
    PrimaryPushButton,
    SegmentedWidget,
)

from D3Mapping.d3_mapping.models.message import MessageInfo
from src.core.bot.bot import Bot
from src.core.signals.global_log_signals import GlobalLogSignals
from src.gui.components.thread_monitor_widget import ThreadMonitorWidget
from src.gui.pages.debugs.listeners_stats import ListenersStatsWidget
from src.gui.pages.debugs.logs import LogsWidget
from src.gui.pages.debugs.message_detail import MessageDetailWidget
from src.gui.pages.debugs.message_table import MessageTable
from src.gui.utils.profiling import profiled_slot


class SnifferWidget(PivotItem):
    msg_table: MessageTable
    msg_detail: MessageDetailWidget
    play_btn: PrimaryPushButton
    stop_btn: PrimaryPushButton

    def __init__(  # type: ignore[override]
        self,
        bot: Bot,
        global_log_signals: GlobalLogSignals,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
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

    def init_top_content(self):
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

        self.rec_start_btn = PrimaryPushButton(
            FluentIcon.MOVIE, "Démarrer enregistrement", top_content
        )
        self.rec_start_btn.clicked.connect(self.on_record_start)

        self.rec_stop_btn = PrimaryPushButton(
            FluentIcon.PAUSE, "Arrêter enregistrement", top_content
        )
        self.rec_stop_btn.clicked.connect(self.on_record_stop)
        self.rec_stop_btn.hide()

        self.rec_save_btn = PrimaryPushButton(
            FluentIcon.SAVE, "Sauvegarder enregistrement", top_content
        )
        self.rec_save_btn.clicked.connect(self.on_record_save)

        if not self.bot.is_fake:
            top_content_layout.addWidget(self.rec_start_btn)
            top_content_layout.addWidget(self.rec_stop_btn)
            top_content_layout.addWidget(self.rec_save_btn)

        if self.bot.is_fake:
            self.rec_replay_btn = PrimaryPushButton(
                FluentIcon.PLAY, "Rejouer un enregistrement", top_content
            )
            self.rec_replay_btn.clicked.connect(self.on_record_replay)
            top_content_layout.addWidget(self.rec_replay_btn)

    def init_content(self):
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

            thread_monitor_widget = ThreadMonitorWidget(
                shared_signals=self.bot.shared_signals, parent=debug_stacked
            )
            debug_stacked.addWidget(thread_monitor_widget)

            debug_pivot.addItem(
                routeKey="logs",
                text="Logs",
                onClick=lambda: debug_stacked.setCurrentWidget(logs_widget),
            )
            debug_pivot.addItem(
                routeKey="listeners",
                text="Listeners",
                onClick=lambda: (
                    debug_stacked.setCurrentWidget(listeners_widget),
                    listeners_widget.init(),
                ),
            )
            debug_pivot.addItem(
                routeKey="threads",
                text="Threads",
                onClick=lambda: debug_stacked.setCurrentWidget(thread_monitor_widget),
            )
            debug_pivot.setCurrentItem("logs")

            self.right_splitter.addWidget(debug_tabs_widget)

            self.logs_widget = logs_widget
            self.listeners_widget = listeners_widget
            self.thread_monitor_widget = thread_monitor_widget
        else:
            self.logs_widget = None
            self.listeners_widget = None
            self.thread_monitor_widget = None

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
    def on_receive_msg_info(self, msg_info: MessageInfo, was_send_from_proxy: bool):
        if self.is_playing:
            self.msg_table.add_row(msg_info, was_send_from_proxy)

    @pyqtSlot()
    def on_play(self):
        self.is_playing = True
        self.play_btn.hide()
        self.stop_btn.show()

    @pyqtSlot()
    def on_stop(self):
        self.is_playing = False
        self.stop_btn.hide()
        self.play_btn.show()

    @pyqtSlot()
    def on_reset(self):
        self.msg_table.table.item_model.remove_rows(
            0, len(self.msg_table.table.item_model._data)
        )
        if self.logs_widget:
            self.logs_widget.logs_table.table.item_model.remove_rows(
                0, len(self.logs_widget.logs_table.table.item_model._data)
            )

    @pyqtSlot(QModelIndex)
    def on_click_msg(self, model_index: QModelIndex):
        source_index = self.msg_table.table.proxy_model.mapToSource(model_index)
        model = self.msg_table.table.item_model
        msg_infos = cast(
            MessageInfo,
            model.data(model.index(source_index.row(), 4), Qt.ItemDataRole.UserRole),
        )
        self.msg_detail.set_content(msg_infos.msg_json, msg_infos.obf_msg_json)
        self.msg_detail.show()

    @pyqtSlot()
    def on_close_detail(self):
        self.msg_detail.hide()

    def on_record_start(self):
        self.bot.recorder.start_session()
        self.rec_start_btn.hide()
        self.rec_stop_btn.show()

    def on_record_stop(self):
        self.bot.recorder.stop_session()
        self.rec_stop_btn.hide()
        self.rec_start_btn.show()

    def on_record_save(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder enregistrement",
            "",
            "JSONL Files (*.jsonl);;All Files (*)",
        )
        if not path:
            return
        self.bot.recorder.save(path)

    def on_record_replay(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un enregistrement",
            "",
            "JSONL Files (*.jsonl);;All Files (*)",
        )
        if not path:
            return
        # emit(path, preserve_timing, speedup, use_obfuscated)
        self.bot.replay_signals.replay_requested.emit(path, False, None, False)
