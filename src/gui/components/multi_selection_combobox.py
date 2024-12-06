from typing import Any, cast, Union

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QWidget
from qfluentwidgets.common import FluentIconBase
from qfluentwidgets.components import ComboBox
from qfluentwidgets.components.widgets.combo_box import ComboBoxMenu, ComboItem


class StayOpenMenu(ComboBoxMenu):
    def _onItemClicked(self, item: Any) -> None:
        action = cast(QAction, item.data(Qt.ItemDataRole.UserRole))
        if action not in self._actions or not action.isEnabled():
            return

        if self.view.itemWidget(item) and not action.property("selectable"):
            return

        # self._hideMenu(False)

        if not self.isSubMenu:
            action.trigger()
            return

        # close parent menu
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
        """
        Retourne une liste contenant la donnée (userData) de chaque item sélectionné.
        """
        return [self.items[i].userData for i in sorted(self.selectedIndices)]

    def _showComboMenu(self) -> None:
        """Affiche un menu déroulant dont les actions sont checkable."""
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

        # Optionnel : ajuster la largeur minimale du menu pour être au moins celle du ComboBox
        if menu.view.width() < self.width():
            menu.view.setMinimumWidth(self.width())
            menu.adjustSize()

        # Configurer le menu pour qu'il se détruise à la fermeture
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(self._onDropMenuClosed)
        self.dropMenu = menu

        # Pour le positionnement, on peut reprendre la méthode originale
        menu_layout = menu.layout()
        left_margin = (
            menu_layout.contentsMargins().left() if menu_layout is not None else 0
        )
        x = -menu.width() // 2 + left_margin + self.width() // 2
        pd = self.mapToGlobal(QPoint(x, self.height()))
        # Ici, pour simplifier, on n'effectue pas d'animation particulière.
        menu.exec(pd)
        # Une fois le menu fermé, on nettoie la référence.
        self.dropMenu = None

    def _onDropMenuClosed(self) -> None:
        self.dropMenu = None

    def _build_toggle_handler(self, index: int) -> Any:
        def _handle_toggle(checked: bool) -> None:
            self._onItemToggled(index, checked)

        return _handle_toggle

    def _onItemToggled(self, index: int, checked: bool) -> None:
        """Met à jour la sélection lors du clic sur une action checkable."""
        if checked:
            self.selectedIndices.add(index)
        else:
            self.selectedIndices.discard(index)
        self._updateDisplayText()
        # Émettre le signal en transmettant la liste des textes sélectionnés.
        selected_texts = [self.items[i].text for i in sorted(self.selectedIndices)]
        self.selectionChanged.emit(selected_texts)

    def _updateDisplayText(self) -> None:
        """Met à jour le texte affiché sur le ComboBox."""
        if self.selectedIndices:
            texts = [self.items[i].text for i in sorted(self.selectedIndices)]
            display_text = ", ".join(texts)
        else:
            display_text = ""
        # Appel à la méthode setText héritée, qui ajuste également la taille.
        self.setText(display_text)

    # Pour éviter le comportement de sélection simple, on surcharge _onItemClicked
    def _onItemClicked(self, index: int) -> None:
        """
        Dans la version multi-sélection, un clic ne doit pas remplacer l'intégralité de la sélection.
        On n'utilise donc pas le comportement de la méthode d'origine.
        """
        # On ne fait rien ici pour empêcher le changement de l'index courant unique.
        pass

    def addItem(
        self,
        text: str,
        icon: Union[str, QIcon, FluentIconBase] | None = None,
        userData: Any = None,
    ) -> None:
        """add item

        Parameters
        ----------
        text: str
            the text of item

        icon: str | QIcon | FluentIconBase
        """
        item = ComboItem(text, icon, userData)  # pyright: ignore[reportArgumentType]
        self.items.append(item)

    # Éventuellement, si tu souhaites autoriser d'autres comportements, tu peux également
    # redéfinir setCurrentIndex() pour qu'il ne fasse rien (puisque la sélection se fait
    # par plusieurs actions).
