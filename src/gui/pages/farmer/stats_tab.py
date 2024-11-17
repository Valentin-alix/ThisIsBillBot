from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import StrongBodyLabel

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from src.controller.farm_stats_controller import FarmStatsController
from src.controller.sale_hotel import SaleHotelController
from src.core.signals.player_signals import GameInfoSignals
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget


class StatsTab(QWidget):
    def __init__(self, character_name: str, game_info_signals: GameInfoSignals):
        super().__init__()
        self.character_name = character_name
        self.game_info_signals = game_info_signals
        self.resource_rows: dict[str, int] = {}
        self._is_loading = False
        self._pending_updates: set[int] = set()

        self.setLayout(QVBoxLayout())

        self.total_value_label = StrongBodyLabel("Valeur totale récoltée: 0 kamas")
        self.layout().addWidget(self.total_value_label)

        self.total_fights_label = StrongBodyLabel("Nombre total de combats: 0")
        self.layout().addWidget(self.total_fights_label)

        self.table_widget = BaseTableWidget()
        columns = [
            ColumnInfo(name="Ressource"),
            ColumnInfo(name="Quantité"),
            ColumnInfo(name="Prix moyen"),
            ColumnInfo(name="Valeur totale"),
        ]
        self.table_widget.table.set_columns(columns)
        self.layout().addWidget(self.table_widget)

        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._process_pending_updates)

        game_info_signals.character_name.connect(self.on_change_character_name)
        self.game_info_signals.resource_harvested.connect(self.on_resource_harvested)
        self.game_info_signals.fight_completed.connect(self.on_fight_completed)

        QTimer.singleShot(0, self.load_initial_data)

    def on_change_character_name(self, character_name: str):
        if self.character_name == character_name:
            return
        self.character_name = character_name
        QTimer.singleShot(0, self.load_initial_data)

    def load_initial_data(self):
        if self._is_loading:
            return

        if not self.character_name:
            return

        self._is_loading = True
        self.clear_table()
        stats = FarmStatsController().get_stats(self.character_name)
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()
        total_value = 0

        for resource_name, quantity in stats.resources_harvested_by_name.items():
            item = DataReader().item_by_name.get(resource_name)
            if not item or not item.id:
                continue

            avg_price = avg_price_by_gid.get(item.id, 0)
            total_item_value = int(quantity * avg_price)
            total_value += total_item_value

            self._add_resource_row(resource_name, quantity, avg_price, total_item_value)

        self.total_value_label.setText(f"Valeur totale récoltée: {total_value:,} kamas")
        self.total_fights_label.setText(
            f"Nombre total de combats: {stats.total_fights}"
        )
        self._is_loading = False

    def clear_table(self):
        self.resource_rows.clear()
        if self.table_widget.table.item_model.rowCount() > 0:
            self.table_widget.table.item_model.clear_all()

    def _add_resource_row(
        self, resource_name: str, quantity: int, avg_price: float, total_value: int
    ):
        row = [
            QStandardItem(resource_name),
            QStandardItem(str(quantity)),
            QStandardItem(f"{int(avg_price):,}"),
            QStandardItem(f"{total_value:,}"),
        ]
        row_index = self.table_widget.table.item_model.rowCount()
        self.resource_rows[resource_name] = row_index
        self.table_widget.table.append_row(row)

    def on_resource_harvested(self, gid: int, _: int):
        self._pending_updates.add(gid)
        if not self._update_timer.isActive():
            self._update_timer.start(200)

    def _process_pending_updates(self):
        if not self._pending_updates:
            return

        stats = FarmStatsController().get_stats(self.character_name)
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()

        for gid in self._pending_updates:
            item = DataReader().item_by_id.get(gid)
            if not item or not item.nameId:
                continue

            resource_name = I18N().name_by_id[item.nameId]
            total_quantity = stats.resources_harvested_by_name.get(resource_name, 0)
            avg_price = avg_price_by_gid.get(gid, 1)
            total_item_value = int(total_quantity * avg_price)

            if resource_name in self.resource_rows:
                self._update_resource_row(
                    resource_name, total_quantity, avg_price, total_item_value
                )
            else:
                self._add_resource_row(
                    resource_name, total_quantity, avg_price, total_item_value
                )

        self._update_total_value()
        self._pending_updates.clear()

    def _update_resource_row(
        self, resource_name: str, quantity: int, avg_price: float, total_value: int
    ):
        row_index = self.resource_rows[resource_name]
        model = self.table_widget.table.item_model
        model.update_row_cells(
            row_index,
            1,
            3,
            [str(quantity), f"{int(avg_price):,}", f"{total_value:,}"],
        )

    def on_fight_completed(self, _: int):
        stats = FarmStatsController().get_stats(self.character_name)
        self.total_fights_label.setText(
            f"Nombre total de combats: {stats.total_fights}"
        )

    def _update_total_value(self):
        stats = FarmStatsController().get_stats(self.character_name)
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()
        total_value = 0

        for resource_name, quantity in stats.resources_harvested_by_name.items():
            item = DataReader().item_by_name.get(resource_name)
            if not item or not item.id:
                continue
            avg_price = avg_price_by_gid.get(item.id, 1)
            total_value += int(quantity * avg_price)

        self.total_value_label.setText(f"Valeur totale récoltée: {total_value:,} kamas")
