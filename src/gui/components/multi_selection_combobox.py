from collections.abc import Callable
from typing import Any
from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget
from qfluentwidgets.common import FluentIconBase
from qfluentwidgets.components import ComboBox
from qfluentwidgets.components.widgets.combo_box import ComboBoxMenu, ComboItem


class StayOpenMenu(ComboBoxMenu):
    def _onItemClicked(self, item: Any) -> None:
        action = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(action, QAction):
            return
        if action not in self._actions or not action.isEnabled():
            return

        if self.view.itemWidget(item) and not action.property("selectable"):
            return

        if not self.isSubMenu:
            action.trigger()
            return

        self._closeParentMenu()
        action.trigger()


class MultiSelectComboBox(ComboBox):
    """
    Version multi-sélection de ComboBox.
    Hérite de ComboBox et modifie le comportement du menu déroulant.
    """

    selectionChanged = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.selectedIndices: set[int] = set()

    def _createComboMenu(self) -> StayOpenMenu:
        return StayOpenMenu(self)

    def selectedItemsData(self) -> list[Any]:
        return [self.items[i].userData for i in sorted(self.selectedIndices)]

    def _showComboMenu(self) -> None:
        if not self.items:
            return

        menu = self._createComboMenu()
        menu.clear()

        for i, item in enumerate(self.items):
            action = QAction(item.icon, item.text, menu)
            action.setCheckable(True)
            action.setChecked(i in self.selectedIndices)
            action.toggled.connect(self._build_toggle_handler(i))
            menu.addAction(action)

        if menu.view.width() < self.width():
            menu.view.setMinimumWidth(self.width())
            menu.adjustSize()

        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(self._onDropMenuClosed)
        self.dropMenu = menu

        menu_layout = menu.layout()
        left_margin = menu_layout.contentsMargins().left() if menu_layout is not None else 0
        x = -menu.width() // 2 + left_margin + self.width() // 2
        pd = self.mapToGlobal(QPoint(x, self.height()))

        menu.exec(pd)

        self.dropMenu = None

    def _onDropMenuClosed(self) -> None:
        self.dropMenu = None

    def _build_toggle_handler(self, index: int) -> Callable[[bool], None]:
        def _handle_toggle(checked: bool) -> None:
            self._onItemToggled(index, checked)

        return _handle_toggle

    def _onItemToggled(self, index: int, checked: bool) -> None:
        if checked:
            self.selectedIndices.add(index)
        else:
            self.selectedIndices.discard(index)
        self._updateDisplayText()

        selected_texts = [self.items[i].text for i in sorted(self.selectedIndices)]
        self.selectionChanged.emit(selected_texts)

    def _updateDisplayText(self) -> None:
        if self.selectedIndices:
            texts = [self.items[i].text for i in sorted(self.selectedIndices)]
            display_text = ", ".join(texts)
        else:
            display_text = ""

        self.setText(display_text)

    def _onItemClicked(self, index: int) -> None:
        """
        Dans la version multi-sélection, un clic ne doit pas remplacer l'intégralité de la sélection.
        On n'utilise donc pas le comportement de la méthode d'origine.
        """

        pass

    def addItem(
        self,
        text: str,
        icon: str | QIcon | FluentIconBase | None = None,
        userData: Any = None,
    ) -> None:
        """add item

        Parameters
        ----------
        text: str
            the text of item

        icon: str | QIcon | FluentIconBase
        """
        item = ComboItem(text, icon, userData)
        self.items.append(item)
