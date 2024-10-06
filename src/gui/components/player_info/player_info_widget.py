from functools import partial
from typing import Any

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.gui.components.player_info.property_group_widget import PropertyGroupWidget
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals


class PlayerInfoWidget(QWidget):
    def __init__(self, grid_signals: GridSignals, game_info_signals: GameInfoSignals):
        super().__init__()
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        self.setLayout(v_layout)

        self.game_info_signals = game_info_signals
        self.grid_signals = grid_signals
        self.group_by_key: dict[str, PropertyGroupWidget] = {}

        self.game_info_signals.character_id.connect(
            partial(self.on_received_property, "Joueur", "Character id")
        )
        self.game_info_signals.breed_id.connect(
            partial(self.on_received_property, "Joueur", "Breed id")
        )
        self.game_info_signals.level.connect(
            partial(self.on_received_property, "Joueur", "Level")
        )
        self.game_info_signals.subscription_end_date.connect(
            partial(self.on_received_property, "Joueur", "Date de fin d'abonnement")
        )
        self.game_info_signals.in_fight.connect(
            partial(self.on_received_property, "Joueur", "Est en combat")
        )
        self.game_info_signals.inventory_weight.connect(
            partial(self.on_received_property, "Joueur", "Poids de l'inventaire")
        )
        self.game_info_signals.weight_max.connect(
            partial(
                self.on_received_property, "Joueur", "Poids maximum de l'inventaire"
            )
        )
        self.grid_signals.new_map_id.connect(
            partial(self.on_received_property, "Map", "Map id")
        )

    @pyqtSlot(str, str, str)
    def on_received_property(self, group_key: str, key: str, value: Any):
        group_widget = self.get_or_create_group_widget(group_key)
        group_widget.add_or_update_property_label(key, str(value))

    def get_or_create_group_widget(self, group_key: str) -> PropertyGroupWidget:
        group_widget = self.group_by_key.get(group_key)
        if group_widget is not None:
            return group_widget

        group_widget = PropertyGroupWidget(key=group_key)
        self.group_by_key[group_key] = group_widget
        self.layout().addWidget(group_widget)

        return group_widget
