from data_center.data_reader import DataReader
from data_center.i18n import I18N
from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import (
    ComboBox,
    FluentIcon,
    PivotItem,
    SegmentedWidget,
    TransparentToolButton,
)

from src.gui.consts import USABLE_BEHAVIORS
from src.gui.pages.farmer.map_tab import MapTab
from src.gui.pages.farmer.player_tab import PlayerTab
from src.gui.pages.farmer.world_tab import WorldTab
from src.gui.utils.run_in_background import Worker
from src.interfaces.enums.bot_action_enum import CraftActionEnum, FarmActionEnum
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


class FarmerWidget(PivotItem):
    play_btn: TransparentToolButton
    stop_btn: TransparentToolButton
    type_action_combo: ComboBox
    area_farm_combo: ComboBox
    sub_area_farm_combo: ComboBox

    _worker_running: tuple[QThread, Worker] | None = None

    def __init__(  # type: ignore
        self,
        login: str,
        grid_signals: GridSignals,
        game_info_signals: GameInfoSignals,
        world_signals: WorldSignals,
        bot_signals: BotSignals,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.login = login
        self.grid_signals = grid_signals
        self.world_signals = world_signals
        self.game_info_signals = game_info_signals
        self.bot_signals = bot_signals

        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        self.setLayout(v_layout)

        self.init_top_content()
        self.init_content()

        self.bot_signals.play_harvester.connect(self.on_play_harvester)
        self.bot_signals.play_crafter.connect(self.on_play_craft)
        self.bot_signals.play_auto_bot.connect(self.on_play_auto)
        self.bot_signals.play_fighter.connect(self.on_play_fighter)

    def init_top_content(self) -> None:
        top_widget = QWidget()
        top_widget.setLayout(QHBoxLayout())

        self.play_btn = TransparentToolButton(FluentIcon.PLAY)
        self.play_btn.clicked.connect(self.on_click_play)
        self.bot_signals.play.connect(self.on_play)
        top_widget.layout().addWidget(self.play_btn)

        self.stop_btn = TransparentToolButton(FluentIcon.PAUSE)
        self.stop_btn.clicked.connect(self.on_click_stop)
        self.bot_signals.stop.connect(self.on_stop)
        top_widget.layout().addWidget(self.stop_btn)
        self.stop_btn.hide()

        self.type_action_combo = ComboBox()
        for farm_action in FarmActionEnum:
            self.type_action_combo.addItem(farm_action)

        for usable_behavior in USABLE_BEHAVIORS:
            self.type_action_combo.addItem(usable_behavior.__name__)

        self.type_action_combo.setCurrentText(FarmActionEnum.HARVESTER)
        self.type_action_combo.currentIndexChanged.connect(self.on_type_action_changed)
        top_widget.layout().addWidget(self.type_action_combo)

        self.sub_area_farm_combo = ComboBox()

        self.area_farm_combo = ComboBox()
        self.area_farm_combo.addItem("")
        self.area_farm_combo.currentIndexChanged.connect(self.on_area_selected)

        for area in sorted(
            DataReader().area_by_id.values(),
            key=lambda area: I18N().name_by_id[area.nameId],
        ):
            self.area_farm_combo.addItem(
                I18N().name_by_id[area.nameId], userData=area.id
            )

        top_widget.layout().addWidget(self.area_farm_combo)

        top_widget.layout().addWidget(self.sub_area_farm_combo)

        self.layout().addWidget(top_widget)

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

        player_tab = PlayerTab(
            grid_signals=self.grid_signals, game_info_signals=self.game_info_signals
        )
        stacked_widget.addWidget(player_tab)
        player_route = f"{self.objectName()}_player_tab"
        pivot.addItem(
            routeKey=player_route,
            text="Joueur",
            onClick=lambda: stacked_widget.setCurrentWidget(player_tab),
        )

        world_tab = WorldTab(world_signals=self.world_signals)
        stacked_widget.addWidget(world_tab)
        world_route = f"{self.objectName()}_world_tab"
        pivot.addItem(
            routeKey=world_route,
            text="Monde",
            onClick=lambda: stacked_widget.setCurrentWidget(world_tab),
        )

    @pyqtSlot()
    def on_type_action_changed(self):
        current_action = self.type_action_combo.currentText()
        if current_action not in FarmActionEnum or current_action in [
            CraftActionEnum.CRAFTER
        ]:
            self.area_farm_combo.setHidden(True)
            self.sub_area_farm_combo.setHidden(True)
        else:
            self.area_farm_combo.setHidden(False)
            self.sub_area_farm_combo.setHidden(False)

        if current_action in [CraftActionEnum.CRAFTER]:
            self.play_btn.setDisabled(True)
        else:
            self.play_btn.setDisabled(False)

    @pyqtSlot()
    def on_area_selected(self):
        current_area_id = self.area_farm_combo.currentData()
        self.sub_area_farm_combo.clear()
        if current_area_id is None:
            return
        self.sub_area_farm_combo.addItem("")
        for sub_area in sorted(
            DataReader().sub_area_by_id.values(),
            key=lambda subarea: I18N().name_by_id[subarea.nameId],
        ):
            if sub_area.areaId != current_area_id:
                continue
            self.sub_area_farm_combo.addItem(
                I18N().name_by_id[sub_area.nameId], userData=sub_area.id
            )

    @pyqtSlot()
    def on_click_play(self):
        area_id = self.area_farm_combo.currentData()
        sub_area_id = self.sub_area_farm_combo.currentData()
        if self.type_action_combo.currentText() == FarmActionEnum.HARVESTER:
            self.bot_signals.play_harvester.emit(area_id, sub_area_id)
        elif self.type_action_combo.currentText() == FarmActionEnum.FIGHTER:
            self.bot_signals.play_fighter.emit(area_id, sub_area_id)
        elif self.type_action_combo.currentText() == FarmActionEnum.AUTO:
            self.bot_signals.play_auto_bot.emit(area_id, sub_area_id)
        elif self.type_action_combo.currentText() not in FarmActionEnum:
            self.bot_signals.play_usable_behavior.emit(
                self.type_action_combo.currentText()
            )

    @pyqtSlot()
    def on_play(self):
        self.stop_btn.show()
        self.play_btn.hide()
        self.type_action_combo.setDisabled(True)
        self.area_farm_combo.setDisabled(True)
        self.sub_area_farm_combo.setDisabled(True)

    @pyqtSlot(object, object)
    def on_play_harvester(self, area_id: int | None, sub_area_id: int | None):
        self.type_action_combo.setCurrentText(FarmActionEnum.HARVESTER)
        self.on_played_zone(area_id, sub_area_id)

    @pyqtSlot(object, object)
    def on_play_fighter(self, area_id: int | None, sub_area_id: int | None, *args):
        self.type_action_combo.setCurrentText(FarmActionEnum.FIGHTER)
        self.on_played_zone(area_id, sub_area_id)

    @pyqtSlot(object, object)
    def on_play_auto(self, area_id: int | None, sub_area_id: int | None):
        self.type_action_combo.setCurrentText(FarmActionEnum.AUTO)
        self.on_played_zone(area_id, sub_area_id)

    @pyqtSlot(object)
    def on_play_craft(self, _):
        self.type_action_combo.addItem(CraftActionEnum.CRAFTER)
        self.type_action_combo.setCurrentText(CraftActionEnum.CRAFTER)

    def on_played_zone(self, area_id: int | None, sub_area_id: int | None):
        if area_id is not None:
            self.area_farm_combo.setCurrentIndex(self.area_farm_combo.findData(area_id))
        else:
            self.area_farm_combo.setCurrentText("")

        if sub_area_id is not None:
            self.sub_area_farm_combo.setCurrentIndex(
                self.sub_area_farm_combo.findData(sub_area_id)
            )
        else:
            self.sub_area_farm_combo.setCurrentText("")

    @pyqtSlot()
    def on_stop(self):
        self.play_btn.show()
        self.stop_btn.hide()
        index_crafter = self.type_action_combo.findText(CraftActionEnum.CRAFTER)
        if index_crafter != -1:
            self.type_action_combo.removeItem(index_crafter)
        self.type_action_combo.setDisabled(False)
        self.area_farm_combo.setDisabled(False)
        self.sub_area_farm_combo.setDisabled(False)

    @pyqtSlot()
    def on_click_stop(self):
        self.bot_signals.stop.emit()
