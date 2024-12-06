from abc import abstractmethod

from PyQt6.QtCore import QObject, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QListView,
    QListWidgetItem,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
)
from qfluentwidgets import ListWidget, LineEdit


class GroupListSignals(QObject):
    clicked_elem_queue = pyqtSignal(object)


class GroupList[T](QGroupBox):
    def __init__(
        self,
        items: list[T],
        is_lazy_loaded: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.is_lazy_loaded = is_lazy_loaded
        self.signals = GroupListSignals(parent=self)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self.input_search: str = ""
        self.widget_by_name: dict[str, QListWidgetItem] = {}
        self.items_by_name: dict[str, T] = {}
        self.list_wid_item = ListWidget(self)
        self.setup_list_items(items)

    def setup_list_items(self, items: list[T]) -> None:
        self.list_wid_item.setLayoutMode(QListView.LayoutMode.Batched)
        self.list_wid_item.setBatchSize(10)
        self.list_wid_item.setUniformItemSizes(True)
        for item in items:
            self.add_item(item)
        self.list_wid_item.itemClicked.connect(self.on_click_item_widget)
        self._layout.addWidget(self.list_wid_item)

        bottom_widget = QWidget(self)
        bottom_widget_layout = QHBoxLayout()
        bottom_widget.setLayout(bottom_widget_layout)

        search_item_edit = LineEdit(bottom_widget)
        search_item_edit.textChanged.connect(self.on_search_changed)
        bottom_widget_layout.addWidget(search_item_edit)

        self._layout.addWidget(bottom_widget)

    @pyqtSlot(QListWidgetItem)
    def on_click_item_widget(self, item: QListWidgetItem):
        name = item.data(Qt.ItemDataRole.UserRole)
        elem = self.items_by_name[name]
        self.signals.clicked_elem_queue.emit(elem)

    @pyqtSlot(str)
    def on_search_changed(self, name: str) -> None:
        self.input_search = name
        self.filter_items()

    def filter_items(self):
        for item in self.items_by_name.values():
            self.handle_item_visibility(item)

    def add_item(self, elem: T) -> None:
        self.items_by_name[self.get_name_item(elem)] = elem
        if not self.is_lazy_loaded:
            self.get_or_create_widget_item(elem)
        self.handle_item_visibility(elem)

    def handle_item_visibility(self, item: T):
        if self.is_lazy_loaded:
            if (
                len(self.input_search) > 2
                and self.input_search.casefold() in self.get_name_item(item).casefold()
            ):
                related_widget = self.get_or_create_widget_item(item)
                related_widget.setHidden(False)
            elif existing_widget := self.widget_by_name.get(self.get_name_item(item)):
                existing_widget.setHidden(True)
        else:
            related_widget = self.get_or_create_widget_item(item)
            if (
                self.input_search == ""
                or self.input_search.casefold() in self.get_name_item(item).casefold()
            ):
                related_widget.setHidden(False)
            else:
                related_widget.setHidden(True)

    def get_or_create_widget_item(self, item: T) -> QListWidgetItem:
        if wid_item := self.widget_by_name.get(self.get_name_item(item)):
            return wid_item
        wid_item = QListWidgetItem(self.get_name_item(item))
        wid_item.setData(Qt.ItemDataRole.UserRole, self.get_name_item(item))
        self.list_wid_item.addItem(wid_item)
        self.widget_by_name[self.get_name_item(item)] = wid_item
        return wid_item

    def remove_item(self, item: T):
        self.items_by_name.pop(self.get_name_item(item))
        related_item = self.widget_by_name.pop(self.get_name_item(item))
        row_index = self.list_wid_item.row(related_item)
        self.list_wid_item.takeItem(row_index)

    @abstractmethod
    def get_name_item(self, item: T) -> str:
        raise NotImplementedError
