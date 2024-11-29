from enum import StrEnum
from typing import cast

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import (
    ComboBox,
    FluentIcon,
    PivotItem,
    SegmentedWidget,
    TransparentToolButton,
)

from src import const
from src.core.behaviors.behavior_factory import USABLE_BEHAVIORS
from src.core.bot.bot import Bot
from src.gui.pages.farmer.inventory_tab import InventoryTab
from src.gui.pages.farmer.map_tab import MapTab
from src.gui.pages.farmer.player_tab import PlayerTab
from src.gui.pages.farmer.world_tab import WorldTab


class FarmActionEnum(StrEnum):
    AUTO = "Automatique"
    HARVESTER = "Récolte"
    FIGHTER = "Combat"


class CraftActionEnum(StrEnum):
    CRAFTER = "Craft"


class FarmerWidget(PivotItem):
    play_btn: TransparentToolButton
    stop_btn: TransparentToolButton
    type_action_combo: ComboBox
    area_farm_combo: ComboBox
    sub_area_farm_combo: ComboBox

    def __init__(  # type: ignore[override]
        self,
        login: str,
        bot: Bot,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.login = login
        self.bot = bot
        self._v_layout = QVBoxLayout()
        self._v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self._v_layout)

        self.map_pivot_item: PivotItem | None = None
        self.player_pivot_item: PivotItem | None = None
        self.world_pivot_item: PivotItem | None = None
        self.inventory_pivot_item: PivotItem | None = None
        self.is_debug_tabs_visible = None

        self.map_tab: MapTab | None = None
        self.player_tab: PlayerTab | None = None
        self.world_tab: WorldTab | None = None
        self.inventory_tab: InventoryTab | None = None

        self.init_top_content()
        self.init_content()

        self.pivot: SegmentedWidget
        self.stacked_widget: QStackedWidget

        self._create_debug_tabs()

        self.bot.bot_signals.play_harvester.connect(self.on_play_harvester)
        self.bot.bot_signals.play_crafter.connect(self.on_play_craft)
        self.bot.bot_signals.play_auto_bot.connect(self.on_play_auto)
        self.bot.bot_signals.play_fighter.connect(self.on_play_fighter)

        self.set_debug_tabs_visibility(const.DEBUG)

    def init_top_content(self) -> None:
        top_widget = QWidget(self)
        top_widget_layout = QHBoxLayout()
        top_widget.setLayout(top_widget_layout)

        self.play_btn = TransparentToolButton(FluentIcon.PLAY, top_widget)
        self.play_btn.clicked.connect(self.on_click_play)
        self.bot.bot_signals.play.connect(self.on_play)
        top_widget_layout.addWidget(self.play_btn)

        self.stop_btn = TransparentToolButton(FluentIcon.PAUSE, top_widget)
        self.stop_btn.clicked.connect(self.on_click_stop)
        self.bot.bot_signals.stop.connect(self.on_stop)
        top_widget_layout.addWidget(self.stop_btn)
        self.stop_btn.hide()

        self.type_action_combo = ComboBox(top_widget)
        for farm_action in FarmActionEnum:
            self.type_action_combo.addItem(farm_action)

        for usable_behavior in USABLE_BEHAVIORS:
            self.type_action_combo.addItem(usable_behavior.__name__)

        self.type_action_combo.setCurrentText(FarmActionEnum.AUTO)
        self.type_action_combo.currentIndexChanged.connect(self.on_type_action_changed)
        top_widget_layout.addWidget(self.type_action_combo)

        self.sub_area_farm_combo = ComboBox(top_widget)

        self.area_farm_combo = ComboBox(top_widget)
        self.area_farm_combo.addItem("")
        self.area_farm_combo.currentIndexChanged.connect(self.on_area_selected)

        for area in sorted(
            DataReader().area_by_id.values(),
            key=lambda area: I18N().name_by_id.get(area.nameId, "Unknown"),
        ):
            self.area_farm_combo.addItem(
                I18N().name_by_id.get(area.nameId, "Unknown"), userData=area.id
            )

        top_widget_layout.addWidget(self.area_farm_combo)

        top_widget_layout.addWidget(self.sub_area_farm_combo)

        self._v_layout.addWidget(top_widget)

    def init_content(self):
        self.pivot = SegmentedWidget(self)
        self._v_layout.addWidget(self.pivot)
        self.stacked_widget = QStackedWidget(self)
        self._v_layout.addWidget(self.stacked_widget)

        # stats_tab = StatsTab(
        #     self.bot.game_state.player.character_name,
        #     self.bot.game_state.player.game_info_signals,
        # )
        # stacked_widget.addWidget(stats_tab)
        # stats_route = f"{self.objectName()}_stats_tab"
        # pivot.addItem(
        #     routeKey=stats_route,
        #     text="Statistiques",
        #     onClick=lambda: stacked_widget.setCurrentWidget(stats_tab),
        # )

    @pyqtSlot()
    def on_type_action_changed(self):
        current_action = self.type_action_combo.currentText()
        if current_action not in FarmActionEnum or current_action in [
            CraftActionEnum.CRAFTER,
            FarmActionEnum.AUTO,
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
            key=lambda subarea: I18N().name_by_id.get(subarea.nameId, ""),
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
        self.bot.bot_signals.play.emit(True)
        if self.type_action_combo.currentText() == FarmActionEnum.HARVESTER:
            self.bot.bot_signals.play_harvester.emit(area_id, sub_area_id)
        elif self.type_action_combo.currentText() == FarmActionEnum.FIGHTER:
            self.bot.bot_signals.play_fighter.emit(area_id, sub_area_id)
        elif self.type_action_combo.currentText() == FarmActionEnum.AUTO:
            self.bot.bot_signals.play_auto_bot.emit()
        elif self.type_action_combo.currentText() not in FarmActionEnum:
            self.bot.bot_signals.play_usable_behavior.emit(
                self.type_action_combo.currentText()
            )

    @pyqtSlot(bool)
    def on_play(self, _):
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

    @pyqtSlot()
    def on_play_auto(self):
        self.type_action_combo.setCurrentText(FarmActionEnum.AUTO)
        self.on_played_zone(None, None)

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
        self.bot.bot_signals.stop.emit()

    def _create_debug_tabs(self) -> None:
        if self.map_tab is not None:
            return

        self.map_tab = MapTab(
            grid_signals=self.bot.grid_signals, parent=self.stacked_widget
        )
        self.stacked_widget.addWidget(self.map_tab)
        self.map_route = f"{self.objectName()}_map_tab"
        self.map_pivot_item = cast(
            PivotItem,
            self.pivot.addItem(
                routeKey=self.map_route,
                text="Map",
                onClick=lambda: self.stacked_widget.setCurrentWidget(self.map_tab),  # type: ignore
            ),
        )

        self.player_tab = PlayerTab(bot=self.bot, parent=self.stacked_widget)
        self.stacked_widget.addWidget(self.player_tab)
        player_route = f"{self.objectName()}_player_tab"
        self.player_pivot_item = cast(
            PivotItem,
            self.pivot.addItem(
                routeKey=player_route,
                text="Joueur",
                onClick=lambda: self.stacked_widget.setCurrentWidget(self.player_tab),  # type: ignore
            ),
        )

        self.world_tab = WorldTab(
            world_signals=self.bot.world_signals, parent=self.stacked_widget
        )
        self.stacked_widget.addWidget(self.world_tab)
        world_route = f"{self.objectName()}_world_tab"
        self.world_pivot_item = cast(
            PivotItem,
            self.pivot.addItem(
                routeKey=world_route,
                text="Monde",
                onClick=lambda: self.stacked_widget.setCurrentWidget(self.world_tab),  # type: ignore
            ),
        )

        self.inventory_tab = InventoryTab(self.bot, parent=self.stacked_widget)
        self.stacked_widget.addWidget(self.inventory_tab)
        inventory_route = f"{self.objectName()}_inventory_tab"
        self.inventory_pivot_item = cast(
            PivotItem,
            self.pivot.addItem(
                routeKey=inventory_route,
                text="Inventaire",
                onClick=lambda: self.stacked_widget.setCurrentWidget(
                    self.inventory_tab  # type: ignore
                ),
            ),
        )

    def set_debug_tabs_visibility(self, is_visible: bool) -> None:
        if self.is_debug_tabs_visible == is_visible:
            return

        self.is_debug_tabs_visible = is_visible

        if is_visible:
            if self.map_pivot_item is not None:
                self.map_pivot_item.setVisible(True)
            if self.player_pivot_item is not None:
                self.player_pivot_item.setVisible(True)
            if self.world_pivot_item is not None:
                self.world_pivot_item.setVisible(True)
            if self.inventory_pivot_item is not None:
                self.inventory_pivot_item.setVisible(True)
            if self.map_tab is not None:
                self.map_tab.setUpdatesEnabled(True)
            if self.player_tab is not None:
                self.player_tab.setUpdatesEnabled(True)
            if self.world_tab is not None:
                self.world_tab.setUpdatesEnabled(True)
            if self.inventory_tab is not None:
                self.inventory_tab.setUpdatesEnabled(True)
                self.inventory_tab.connect_signals()
            self.pivot.setCurrentItem(self.map_route)
            assert self.map_tab
            self.stacked_widget.setCurrentWidget(self.map_tab)
        else:
            if self.map_pivot_item is not None:
                self.map_pivot_item.setVisible(False)
            if self.player_pivot_item is not None:
                self.player_pivot_item.setVisible(False)
            if self.world_pivot_item is not None:
                self.world_pivot_item.setVisible(False)
            if self.inventory_pivot_item is not None:
                self.inventory_pivot_item.setVisible(False)
            if self.map_tab is not None:
                self.map_tab.setUpdatesEnabled(False)
            if self.player_tab is not None:
                self.player_tab.setUpdatesEnabled(False)
            if self.world_tab is not None:
                self.world_tab.setUpdatesEnabled(False)
            if self.inventory_tab is not None:
                self.inventory_tab.setUpdatesEnabled(False)
                self.inventory_tab.disconnect_signals()
