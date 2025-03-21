from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.core.signals.grid_signals import GridSignals
from src.core.states.game_state import GameState
from src.gui.components.graphics.grid_widget import GridView
from src.gui.components.qfluent_widget.scrollable_message_box import (
    ScrollableMessageBox,
)


class MapTab(QWidget):
    def __init__(
        self,
        grid_signals: GridSignals,
        game_state: GameState,
        parent: QWidget | None = None,
    ):
        super().__init__(parent=parent)
        self.grid_signals = grid_signals
        self.game_state = game_state

        layout = QVBoxLayout()
        self.setLayout(layout)
        scroll_area_info = SingleDirectionScrollArea(self)

        content_widget = QWidget(scroll_area_info)
        content_widget_layout = QHBoxLayout()
        content_widget.setLayout(content_widget_layout)

        grid_view = GridView(grid_signals)
        content_widget_layout.addWidget(grid_view)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(content_widget)
        scroll_area_info.enableTransparentBackground()

        layout.addWidget(scroll_area_info)

        self.grid_signals.cell_id_clicked.connect(self.on_cell_id_clicked)

    @pyqtSlot(int)
    def on_cell_id_clicked(self, cell_id: int) -> None:
        actor = self.game_state.entity.get_first_actor_on_cell_id(cell_id)

        if actor is not None:
            if actor.actor_id in self.game_state.entity.actor_fight_by_id:
                content = str(self.game_state.entity.actor_fight_by_id[actor.actor_id])
            else:
                content = str(actor)
            ScrollableMessageBox(f"Acteur sur cell {cell_id}", content, self).exec()
            return

        stated_elements = self.game_state.interactive.stated_element_by_cell_id.get(
            cell_id
        )
        if stated_elements:
            stated_element, collectable = next(iter(stated_elements.values()))
            content = str(stated_element)
            if collectable is not None:
                content += f"\n\nCollectable: {collectable}"
            ScrollableMessageBox(
                f"Interactive sur cell {cell_id}", content, self
            ).exec()
