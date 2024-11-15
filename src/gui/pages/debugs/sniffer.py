from functools import partial

from d3_mapping.models.message import MessageInfo
from PyQt5.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import FluentIcon, LineEdit, PivotItem, PrimaryPushButton

from src.bot import Bot
from src.gui.pages.debugs.logs import LogsWidget
from src.gui.pages.debugs.message_detail import MessageDetailWidget
from src.gui.pages.debugs.message_table import MessageTable
from src.gui.utils.profiling import profiled_slot


class SnifferWidget(PivotItem):  # type: ignore
    msg_table: MessageTable
    msg_detail: MessageDetailWidget
    play_btn: PrimaryPushButton
    stop_btn: PrimaryPushButton

    def __init__(  # type: ignore
        self,
        bot: Bot,
        *args,
        **kwargs,
    ):  # type: ignore
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.is_playing: bool = True
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 4, 4, 4)
        self.v_layout.setSpacing(0)
        self.setLayout(self.v_layout)
        self.init_top_content()
        self.init_content()

        self.bot.msg_info_signals.clear_msg_infos.connect(self.on_reset)
        self.bot.msg_info_signals.msg_info.connect(
            profiled_slot(self.on_receive_msg_info)
        )

    def init_top_content(self):
        top_content = QWidget()
        # prevent top header from expanding in height
        top_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout().addWidget(top_content)
        top_content.setLayout(QHBoxLayout())
        top_content.layout().setContentsMargins(0, 0, 0, 0)
        reset_btn = PrimaryPushButton(FluentIcon.DELETE, "Réinitialiser")
        reset_btn.clicked.connect(self.on_reset)
        top_content.layout().addWidget(reset_btn)

        self.play_btn = PrimaryPushButton(FluentIcon.PLAY, "Lancer le sniffer")
        if self.is_playing:
            self.play_btn.hide()
        self.play_btn.clicked.connect(self.on_play)
        top_content.layout().addWidget(self.play_btn)

        self.stop_btn = PrimaryPushButton(FluentIcon.PAUSE, "Arrêter le sniffer")
        if not self.is_playing:
            self.stop_btn.hide()
        self.stop_btn.clicked.connect(self.on_stop)
        top_content.layout().addWidget(self.stop_btn)

        self.rec_start_btn = PrimaryPushButton(
            FluentIcon.MOVIE, "Démarrer enregistrement"
        )
        self.rec_start_btn.clicked.connect(self.on_record_start)

        self.rec_stop_btn = PrimaryPushButton(
            FluentIcon.PAUSE, "Arrêter enregistrement"
        )
        self.rec_stop_btn.clicked.connect(self.on_record_stop)
        self.rec_stop_btn.hide()

        self.rec_save_btn = PrimaryPushButton(
            FluentIcon.SAVE, "Sauvegarder enregistrement"
        )
        self.rec_save_btn.clicked.connect(self.on_record_save)

        if not self.bot.is_fake:
            top_content.layout().addWidget(self.rec_start_btn)
            top_content.layout().addWidget(self.rec_stop_btn)
            top_content.layout().addWidget(self.rec_save_btn)

        if self.bot.is_fake:
            self.rec_replay_btn = PrimaryPushButton(
                FluentIcon.PLAY, "Rejouer un enregistrement"
            )
            self.rec_replay_btn.clicked.connect(self.on_record_replay)
            top_content.layout().addWidget(self.rec_replay_btn)

    def init_content(self):
        content = QWidget()
        content.setLayout(QHBoxLayout())
        content.layout().setSpacing(0)
        content.layout().setContentsMargins(0, 0, 0, 0)

        # left side: filter + message table
        self.msg_table = MessageTable()
        self.msg_table.table.clicked.connect(self.on_click_msg)

        left_widget = QWidget()
        left_widget.setLayout(QVBoxLayout())
        left_widget.layout().setContentsMargins(0, 0, 0, 0)
        left_widget.layout().setSpacing(0)

        wrapper_filter = QWidget()
        wrapper_filter.setLayout(QHBoxLayout())
        # filter bar should not expand vertically
        wrapper_filter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        wrapper_filter.layout().setContentsMargins(0, 16, 0, 0)
        custom_filter = LineEdit()
        wrapper_filter.layout().addWidget(custom_filter)
        custom_filter.setPlaceholderText("Contenu")
        custom_filter.textChanged.connect(
            partial(self.msg_table.table.header.on_new_filter_input, 4)
        )

        left_widget.layout().addWidget(wrapper_filter)
        left_widget.layout().addWidget(self.msg_table)
        left_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.msg_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # right side: message detail and logs
        self.msg_detail = MessageDetailWidget()
        self.msg_detail.hide()
        self.msg_detail.quit_btn.clicked.connect(self.on_close_detail)

        self.right_splitter = QSplitter(Qt.Vertical)
        self.right_splitter.addWidget(self.msg_detail)
        if self.bot.log_signals is not None:
            self.logs_widget = LogsWidget(log_signals=self.bot.log_signals)
            # make logs expand to fill splitter space
            self.logs_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.right_splitter.addWidget(self.logs_widget)
        else:
            self.logs_widget = None

        # main horizontal splitter: left (filter+table) | right (detail+logs)
        splitter = QSplitter(Qt.Horizontal)
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

        content.layout().addWidget(splitter)
        self.layout().addWidget(content)

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
        msg_infos: MessageInfo = model.data(
            model.index(source_index.row(), 4), Qt.UserRole
        )  # type: ignore
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
        self.bot.replay_signals.replay_requested.emit(path)
