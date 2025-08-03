from datetime import datetime

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel

from src import const
from src.core.bot.bot import Bot

_UNKNOWN_VALUE = "—"


class AccountQuickInfoWidget(QWidget):
    def __init__(self, bot: Bot, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.bot = bot

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.setLayout(layout)

        self.subscription_end_label = self._add_info_column(layout, "Fin d'abonnement")
        self.kamas_label = self._add_info_column(layout, "Kamas")
        self.level_label = self._add_info_column(layout, "Niveau")
        self.sub_area_label = self._add_info_column(layout, "Sous-zone actuelle")

        self.bot.game_info_signals.subscription_end_date.connect(self._set_subscription_end_date)
        self.bot.inventory_signals.kamas.connect(self._set_kamas)
        self.bot.game_info_signals.level.connect(self._set_level)
        self.bot.grid_signals.new_map_id.connect(self._set_sub_area)
        self.bot.game_info_signals.is_ready_to_play.connect(self._sync_from_state)

        self._set_subscription_end_date(self.bot.game_state.player.subscription_end_date)
        if self.bot.is_ready_to_play_event.is_set():
            self._sync_game_values_from_state()

    @staticmethod
    def _add_info_column(layout: QHBoxLayout, title: str) -> BodyLabel:
        column_widget = QWidget()
        column_layout = QVBoxLayout()
        column_layout.setContentsMargins(0, 2, 0, 2)
        column_layout.setSpacing(0)
        column_widget.setLayout(column_layout)

        title_label = CaptionLabel(text=title, parent=column_widget)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        column_layout.addWidget(title_label)

        value_label = BodyLabel(text=_UNKNOWN_VALUE, parent=column_widget)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setWordWrap(True)
        value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        column_layout.addWidget(value_label)

        layout.addWidget(column_widget, 1)
        return value_label

    def _sync_from_state(self) -> None:
        self._set_subscription_end_date(self.bot.game_state.player.subscription_end_date)
        self._sync_game_values_from_state()

    def _sync_game_values_from_state(self) -> None:
        self._set_kamas(self.bot.game_state.inventory.kamas)
        self._set_level(self.bot.game_state.player.level)
        self._set_sub_area(self.bot.game_state.map.map_id)

    def _set_subscription_end_date(self, subscription_end_date: datetime) -> None:
        if subscription_end_date == const.MIN_DATE:
            self.subscription_end_label.setText(_UNKNOWN_VALUE)
            return
        self.subscription_end_label.setText(subscription_end_date.strftime("%d/%m/%Y %H:%M"))

    def _set_kamas(self, kamas: int) -> None:
        self.kamas_label.setText(f"{kamas:,}".replace(",", " "))

    def _set_level(self, level: int) -> None:
        self.level_label.setText(str(level))

    def _set_sub_area(self, map_id: int) -> None:
        if map_id == 0:
            self.sub_area_label.setText(_UNKNOWN_VALUE)
            return
        map_position = DataReader().map_info_by_map_id[map_id]
        sub_area = DataReader().sub_area_by_id[map_position.subAreaId]
        self.sub_area_label.setText(I18N().name_by_id[sub_area.nameId])
