from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import PivotItem, FluentIcon, TransparentToolButton

from src.gui.components.player_info_widget import PlayerInfoWidget
from src.signals.harvester_signals import HarvesterSignals
from src.signals.player_signals import StatePropertySignals


class HarvesterWidget(PivotItem):
    play_btn: TransparentToolButton
    stop_btn: TransparentToolButton

    def __init__(
        self,
        player_property_signals: StatePropertySignals,
        harvester_signals: HarvesterSignals,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.player_property_signals = player_property_signals
        self.harvester_signals = harvester_signals

        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        self.setLayout(v_layout)

        self.init_content()

    def init_content(self):
        top_widget = QWidget()
        top_widget.setLayout(QHBoxLayout())

        self.play_btn = TransparentToolButton(FluentIcon.PLAY)
        self.play_btn.clicked.connect(self.on_play)
        top_widget.layout().addWidget(self.play_btn)

        self.stop_btn = TransparentToolButton(FluentIcon.PAUSE)
        self.stop_btn.clicked.connect(self.on_stop)
        top_widget.layout().addWidget(self.stop_btn)
        self.stop_btn.hide()

        self.layout().addWidget(top_widget)

        self.layout().addWidget(PlayerInfoWidget(self.player_property_signals))

    def on_play(self):
        self.stop_btn.show()
        self.play_btn.hide()
        self.harvester_signals.play.emit()

    def on_stop(self):
        self.play_btn.show()
        self.stop_btn.hide()
        self.harvester_signals.stop.emit()
