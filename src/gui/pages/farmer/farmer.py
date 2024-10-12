from enum import StrEnum

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QStackedWidget
from qfluentwidgets import (
    PivotItem,
    FluentIcon,
    TransparentToolButton,
    ComboBox,
    SegmentedWidget,
)

from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.gui.pages.farmer.map_tab import MapTab
from src.gui.pages.farmer.world_tab import WorldTab
from src.gui.utils.run_in_background import Worker
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.shared_farm_signals import SharedFarmSignals
from src.signals.world_signals import WorldSignals


class FarmActionEnum(StrEnum):
    HARVESTER = "Récolte"
    FIGHTER = "Combat"
    # MULE_FIGHTER = "Mule Fighter"


class FarmerWidget(PivotItem):
    play_btn: TransparentToolButton
    stop_btn: TransparentToolButton
    type_action_combo: ComboBox
    area_farm_combo: ComboBox
    sub_area_farm_combo: ComboBox

    _worker_running: tuple[QThread, Worker] | None = None

    def __init__(
        self,
        account_id: int,
        grid_signals: GridSignals,
        game_info_signals: GameInfoSignals,
        world_signals: WorldSignals,
        farm_signals: BotSignals,
        shared_farm_signals: SharedFarmSignals,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.account_id = account_id
        self.grid_signals = grid_signals
        self.world_signals = world_signals
        self.game_info_signals = game_info_signals
        self.farm_signals = farm_signals
        self.shared_farm_signals = shared_farm_signals

        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        self.setLayout(v_layout)

        self.init_top_content()
        self.init_content()

    def init_top_content(self) -> None:
        top_widget = QWidget()
        top_widget.setLayout(QHBoxLayout())

        self.play_btn = TransparentToolButton(FluentIcon.PLAY)
        self.play_btn.clicked.connect(self.on_click_play)
        self.farm_signals.play.connect(self.on_play)
        top_widget.layout().addWidget(self.play_btn)

        self.stop_btn = TransparentToolButton(FluentIcon.PAUSE)
        self.game_info_signals.disconnected.connect(self.on_click_stop)
        self.stop_btn.clicked.connect(self.on_click_stop)
        self.farm_signals.stop.connect(self.on_stop)
        top_widget.layout().addWidget(self.stop_btn)
        self.stop_btn.hide()

        self.type_action_combo = ComboBox()
        for farm_action in FarmActionEnum:
            self.type_action_combo.addItem(farm_action)
        self.type_action_combo.setCurrentText(FarmActionEnum.HARVESTER)
        top_widget.layout().addWidget(self.type_action_combo)

        self.sub_area_farm_combo = ComboBox()

        self.area_farm_combo = ComboBox()
        self.area_farm_combo.addItem("")
        self.area_farm_combo.currentIndexChanged.connect(self.on_area_selected)

        for area in sorted(
            DataReader().area_by_id.values(),
            key=lambda area: I18N.name_by_id[area.nameId],
        ):
            self.area_farm_combo.addItem(I18N.name_by_id[area.nameId], userData=area.id)

        top_widget.layout().addWidget(self.area_farm_combo)

        top_widget.layout().addWidget(self.sub_area_farm_combo)

        self.layout().addWidget(top_widget)

    def on_area_selected(self):
        current_area_id = self.area_farm_combo.currentData()
        self.sub_area_farm_combo.clear()
        if current_area_id is None:
            return
        self.sub_area_farm_combo.addItem("")
        for sub_area in sorted(
            DataReader().sub_area_by_id.values(),
            key=lambda subarea: I18N.name_by_id[subarea.nameId],
        ):
            if sub_area.areaId != current_area_id:
                continue
            self.sub_area_farm_combo.addItem(
                I18N.name_by_id[sub_area.nameId], userData=sub_area.id
            )

    def init_content(self):
        pivot = SegmentedWidget()
        self.layout().addWidget(pivot)
        stacked_widget = QStackedWidget(self)
        self.layout().addWidget(stacked_widget)

        map_tab = MapTab(
            grid_signals=self.grid_signals, game_info_signals=self.game_info_signals
        )
        stacked_widget.addWidget(map_tab)
        map_route = f"{self.objectName()}_map_tab"
        pivot.addItem(
            routeKey=map_route,
            text="Map",
            onClick=lambda: stacked_widget.setCurrentWidget(map_tab),
        )
        pivot.setCurrentItem(map_route)

        world_tab = WorldTab(world_signals=self.world_signals)
        stacked_widget.addWidget(world_tab)
        world_route = f"{self.objectName()}_world_tab"
        pivot.addItem(
            routeKey=world_route,
            text="Monde",
            onClick=lambda: stacked_widget.setCurrentWidget(world_tab),
        )

    def on_play(self):
        self.stop_btn.show()
        self.play_btn.hide()

    def on_click_play(self):
        self.on_play()
        area_id = self.area_farm_combo.currentData()
        sub_area_id = self.sub_area_farm_combo.currentData()
        if self.type_action_combo.currentText() == FarmActionEnum.HARVESTER:
            self.farm_signals.play_harvester.emit(area_id, sub_area_id)

        elif self.type_action_combo.currentText() == FarmActionEnum.FIGHTER:
            self.shared_farm_signals.play_fighter.emit(
                self.account_id, area_id, sub_area_id, None
            )

    def on_stop(self):
        self.play_btn.show()
        self.stop_btn.hide()

    def on_click_stop(self):
        self.farm_signals.stop.emit()
