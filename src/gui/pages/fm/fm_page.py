from logging import Logger

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, TransparentToolButton

from src.core.signals.bot_signals import BotSignals
from src.gui.pages.fm.fm_item.fm_item import FmItem


class FmPage(QWidget):
    def __init__(
        self,
        logger: Logger,
        bot_signals: BotSignals,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_run: QThread | None = None
        self.thread_stop: QThread | None = None
        self.logger = logger
        self.bot_signals = bot_signals
        self.curr_fm_item: FmItem | None = None

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.main_layout)

        self._setup_action_widget()
        self._setup_content()

    def _setup_action_widget(self):
        self.play_btn = TransparentToolButton(FluentIcon.PLAY, self)
        # self.bot_signals.play.connect(self.on_play)
        # self.play_btn.clicked.connect(self.on_click_play)
        self.main_layout.addWidget(self.play_btn)

        self.stop_btn = TransparentToolButton(FluentIcon.PAUSE, self)
        # self.bot_signals.stop.connect(self.on_stop)
        # self.stop_btn.clicked.connect(self.on_click_stop)
        self.main_layout.addWidget(self.stop_btn)
        self.stop_btn.hide()

    def _setup_content(self) -> None:
        content_widget = QWidget(self)
        self.main_layout.addWidget(content_widget)
        self.content_widget_layout = QVBoxLayout()
        content_widget.setLayout(self.content_widget_layout)
