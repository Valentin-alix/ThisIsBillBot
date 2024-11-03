from functools import partial

from PyQt5.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QSplitter, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, LineEdit, PivotItem, PrimaryPushButton

from d3_mapping.gui.sniffer.message_detail import MessageDetailWidget
from d3_mapping.gui.sniffer.message_table import MessageTable
from d3_mapping.models.message import MessageInfo
from d3_mapping.signals.message_signals import MessageInfoSignals


class SnifferWidget(PivotItem):  # type: ignore
    msg_table: MessageTable
    msg_detail: MessageDetailWidget
    play_btn: PrimaryPushButton
    stop_btn: PrimaryPushButton

    def __init__(self, message_info_signals: MessageInfoSignals, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.is_playing: bool = True
        self.message_info_signals = message_info_signals
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 4, 4, 4)
        self.v_layout.setSpacing(0)
        self.setLayout(self.v_layout)
        self.init_top_content()
        self.init_content()

        self.message_info_signals.msg_info.connect(self.on_receive_msg_info)

    def init_top_content(self):
        top_content = QWidget()
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

    def init_content(self):
        content = QWidget()
        content.setLayout(QHBoxLayout())
        content.layout().setSpacing(0)
        content.layout().setContentsMargins(0, 0, 0, 0)

        self.msg_table = MessageTable()
        self.msg_table.table.clicked.connect(self.on_click_msg)

        self.msg_detail = MessageDetailWidget()
        self.msg_detail.hide()
        self.msg_detail.quit_btn.clicked.connect(self.on_close_detail)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.msg_table)
        splitter.addWidget(self.msg_detail)
        content.layout().addWidget(splitter)

        wrapper_filter = QWidget()
        wrapper_filter.setLayout(QHBoxLayout())
        wrapper_filter.layout().setContentsMargins(0, 16, 0, 0)
        custom_filter = LineEdit()
        wrapper_filter.layout().addWidget(custom_filter)
        custom_filter.setPlaceholderText("Contenu")
        custom_filter.textChanged.connect(
            partial(self.msg_table.table.header.on_new_filter_input, 3)
        )
        self.layout().addWidget(wrapper_filter)

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

    @pyqtSlot(QModelIndex)
    def on_click_msg(self, model_index: QModelIndex):
        source_index = self.msg_table.table.proxy_model.mapToSource(model_index)
        model = self.msg_table.table.item_model
        msg_infos: MessageInfo = model.data(
            model.index(source_index.row(), 3), Qt.UserRole
        )  # type: ignore
        self.msg_detail.set_content(
            msg_infos.msg_json, msg_infos.obf_msg_json, msg_infos.raw_content
        )
        self.msg_detail.show()

    @pyqtSlot()
    def on_close_detail(self):
        self.msg_detail.hide()
