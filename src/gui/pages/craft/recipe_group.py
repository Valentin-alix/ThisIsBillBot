from functools import cache

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
from DBDofusUnity.dofus_unity_reader.models.datas.recipe_root import RecipeItem
from PyQt6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QSortFilterProxyModel,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtWidgets import QHBoxLayout, QListView, QVBoxLayout, QWidget
from qfluentwidgets import LineEdit


class RecipeGroupSignals(QObject):
    clicked_elem_queue = pyqtSignal(object)


class RecipeCatalogModel(QAbstractListModel):
    def __init__(self) -> None:
        super().__init__()
        reader = DataReader()
        self.recipes = reader.recipes
        self.names = [
            I18N().name_by_id.get(reader.item_by_id[recipe.resultId].nameId, "")
            if reader.item_by_id[recipe.resultId].nameId
            else ""
            for recipe in self.recipes
        ]
        self.normalized_names = [name.casefold() for name in self.names]

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self.recipes)

    def data(self, index: QModelIndex, role: int | None = None) -> object | None:
        if not index.isValid():
            return None
        if role in (None, Qt.ItemDataRole.DisplayRole):
            return self.names[index.row()]
        if role == Qt.ItemDataRole.UserRole:
            return self.recipes[index.row()]
        return None


@cache
def recipe_catalog_model() -> RecipeCatalogModel:
    return RecipeCatalogModel()


class RecipeFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.catalog = recipe_catalog_model()
        self.query = ""
        self.excluded_recipes: set[RecipeItem] = set()
        self.setSourceModel(self.catalog)

    def set_query(self, query: str) -> None:
        self.query = query.casefold()
        self.invalidateFilter()

    def set_recipe_excluded(self, recipe: RecipeItem, excluded: bool) -> None:
        if excluded:
            self.excluded_recipes.add(recipe)
        else:
            self.excluded_recipes.discard(recipe)
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if len(self.query) <= 2:
            return False
        return (
            self.catalog.recipes[source_row] not in self.excluded_recipes
            and self.query in self.catalog.normalized_names[source_row]
        )


class RecipeGroup(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.signals = RecipeGroupSignals(parent=self)
        self.proxy_model = RecipeFilterProxyModel(self)

        layout = QVBoxLayout(self)
        self.list_view = QListView(self)
        self.list_view.setUniformItemSizes(True)
        self.list_view.setModel(self.proxy_model)
        self.list_view.clicked.connect(self._on_clicked)
        layout.addWidget(self.list_view)

        search_wrapper = QWidget(self)
        search_layout = QHBoxLayout(search_wrapper)
        self.search_edit = LineEdit(search_wrapper)
        search_layout.addWidget(self.search_edit)
        layout.addWidget(search_wrapper)

        self._search_timer = QTimer(self)
        self._search_timer.setInterval(250)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_search)
        self.search_edit.textChanged.connect(self._search_timer.start)

    def add_item(self, recipe: RecipeItem) -> None:
        self.proxy_model.set_recipe_excluded(recipe, False)

    def remove_item(self, recipe: RecipeItem) -> None:
        self.proxy_model.set_recipe_excluded(recipe, True)

    def _apply_search(self) -> None:
        self.proxy_model.set_query(self.search_edit.text())

    def _on_clicked(self, index: QModelIndex) -> None:
        recipe = self.proxy_model.data(index, Qt.ItemDataRole.UserRole)
        if not isinstance(recipe, RecipeItem):
            raise TypeError("Expected a RecipeItem payload in the recipe catalog")
        self.signals.clicked_elem_queue.emit(recipe)
