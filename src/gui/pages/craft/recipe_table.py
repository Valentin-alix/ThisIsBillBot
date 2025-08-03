from collections.abc import KeysView

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.models.datas.recipe_root import RecipeItem
from PyQt6 import QtWidgets
from PyQt6.QtCore import QModelIndex, QObject, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QWidget

from src.core.engine.crafts.recipes import get_benefice_on_craft_recipe
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget


def _require_recipe_item(value: object) -> RecipeItem:
    if not isinstance(value, RecipeItem):
        raise TypeError("Expected a RecipeItem payload in the recipe table model")
    return value


class RecipeTableSignals(QObject):
    removed_recipe = pyqtSignal(RecipeItem)


class RecipeTable(BaseTableWidget):
    def __init__(self, recipes: list[RecipeItem], parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Nom"),
            ColumnInfo(name="Métier"),
            ColumnInfo(name="Lvl"),
            ColumnInfo(name="Bénéfice"),
        ]
        self.table.set_columns(columns)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        self.signals = RecipeTableSignals(parent=self)
        self.widget_item_by_recipe: dict[RecipeItem, QStandardItem] = {}
        for recipe in recipes:
            self.add_recipe(recipe)

        self.table.clicked.connect(self.on_click_recipe)

    @property
    def recipes(self) -> KeysView[RecipeItem]:
        return self.widget_item_by_recipe.keys()

    def add_recipe(self, recipe: RecipeItem) -> None:
        name_id = DataReader().item_by_id[recipe.resultId].nameId
        recipe_widget_item = QStandardItem(I18N().name_by_id[name_id] if name_id else "")
        recipe_widget_item.setData(recipe, role=Qt.ItemDataRole.UserRole)
        self.widget_item_by_recipe[recipe] = recipe_widget_item

        job_name_widget = QStandardItem(I18N().name_by_id[DataReader().job_by_id[recipe.jobId].nameId])

        recipe_lvl = QStandardItem(str(DataReader().item_by_id[recipe.resultId].level))

        profit = get_benefice_on_craft_recipe(recipe) or "Unknown"
        benefice = QStandardItem(str(profit))

        self.table.item_model.append_row([recipe_widget_item, job_name_widget, recipe_lvl, benefice])

    @pyqtSlot(QModelIndex)
    def on_click_recipe(self, model_index: QModelIndex) -> None:
        source_index = self.table.proxy_model.mapToSource(model_index)
        model = self.table.item_model
        recipe = _require_recipe_item(
            model.data(model.index(source_index.row(), 0), Qt.ItemDataRole.UserRole)
        )
        model.remove_rows(source_index.row(), 1)
        self.on_remove_recipe(recipe)

    def on_remove_recipe(self, recipe: RecipeItem) -> None:
        self.signals.removed_recipe.emit(recipe)
        self.widget_item_by_recipe.pop(recipe)
