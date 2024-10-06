from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    PivotItem,
    FluentIcon,
    TransparentToolButton,
    SingleDirectionScrollArea,
    SmoothMode,
)

from src.gui.components.grid_widget import GridView
from src.gui.components.player_info.player_info_widget import PlayerInfoWidget
from src.signals.grid_signals import GridSignals
from src.signals.harvester_signals import HarvesterSignals
from src.signals.player_signals import GameInfoSignals


class FarmerWidget(PivotItem):
    play_btn: TransparentToolButton
    stop_btn: TransparentToolButton

    def __init__(
        self,
        grid_signals: GridSignals,
        game_info_signals: GameInfoSignals,
        harvester_signals: HarvesterSignals,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.grid_signals = grid_signals
        self.game_info_signals = game_info_signals
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

        scroll_area_info = SingleDirectionScrollArea()

        content_widget = QWidget()
        content_widget.setLayout(QHBoxLayout())

        grid_view = GridView(self.grid_signals)
        content_widget.layout().addWidget(grid_view)

        player_info_widget = PlayerInfoWidget(self.grid_signals, self.game_info_signals)
        content_widget.layout().addWidget(player_info_widget)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(content_widget)
        scroll_area_info.enableTransparentBackground()

        self.layout().addWidget(scroll_area_info)

    def on_play(self):
        self.stop_btn.show()
        self.play_btn.hide()
        self.harvester_signals.play.emit()

    def on_stop(self):
        self.play_btn.show()
        self.stop_btn.hide()
        self.harvester_signals.stop.emit()
