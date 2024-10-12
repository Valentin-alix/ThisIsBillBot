from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QModelIndex, Qt
from PyQt5.QtGui import QStandardItem

from models.datas.recipe_root import RecipeItem
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget


class RecipeTableSignals(QObject):
    removed_recipe = pyqtSignal(object)


class RecipeTable(BaseTableWidget):
    def __init__(self, recipes: list[RecipeItem]) -> None:
        super().__init__()
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Nom"),
            ColumnInfo(name="Métier"),
            ColumnInfo(name="Lvl"),
        ]
        self.table.set_columns(columns)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.signals = RecipeTableSignals()
        self.widget_item_by_recipe: dict[RecipeItem, QStandardItem] = {}
        for recipe in recipes:
            self.add_recipe(recipe)

        self.table.clicked.connect(self.on_click_recipe)

    @property
    def recipes(self):
        return self.widget_item_by_recipe.keys()

    def add_recipe(self, recipe: RecipeItem) -> None:
        recipe_widget_item = QStandardItem(
            I18N.name_by_id[DataReader().item_by_id[recipe.resultId].nameId]
        )
        recipe_widget_item.setData(recipe, role=Qt.UserRole)
        self.widget_item_by_recipe[recipe] = recipe_widget_item

        job_name_widget = QStandardItem(
            I18N.name_by_id[DataReader().job_by_id[recipe.jobId].nameId]
        )

        recipe_lvl = QStandardItem(str(DataReader().item_by_id[recipe.resultId].level))
        self.table.item_model.append_row(
            [recipe_widget_item, job_name_widget, recipe_lvl]
        )

    @pyqtSlot(QModelIndex)
    def on_click_recipe(self, model_index: QModelIndex):
        source_index = self.table.proxy_model.mapToSource(model_index)
        model = self.table.item_model
        recipe: RecipeItem = model.data(model.index(source_index.row(), 0), Qt.UserRole)
        model.remove_rows(source_index.row(), 1)
        self.on_remove_recipe(recipe)

    def on_remove_recipe(self, recipe: RecipeItem) -> None:
        self.signals.removed_recipe.emit(recipe)
        self.widget_item_by_recipe.pop(recipe)
