from functools import partial
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.gui.pages.farmer.player_info.property_group_widget import PropertyGroupWidget
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals


class PlayerInfoWidget(QWidget):
    def __init__(self, grid_signals: GridSignals, game_info_signals: GameInfoSignals):
        super().__init__()
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        self.setLayout(v_layout)

        self.inventory_weight: int = 0
        self.weight_max: int = 0

        self.game_info_signals = game_info_signals
        self.grid_signals = grid_signals
        self.group_by_key: dict[str, PropertyGroupWidget] = {}

        self.game_info_signals.character_id.connect(
            partial(self.on_received_property, "Joueur", "Player id")
        )
        self.game_info_signals.character_name.connect(
            partial(self.on_received_property, "Joueur", "Nom")
        )
        self.game_info_signals.breed_id.connect(
            partial(self.on_received_property, "Joueur", "Race id")
        )
        self.game_info_signals.level.connect(
            partial(self.on_received_property, "Joueur", "Niveau")
        )
        self.game_info_signals.subscription_end_date.connect(
            partial(self.on_received_property, "Joueur", "Date de fin d'abonnement")
        )
        self.game_info_signals.in_fight.connect(
            partial(self.on_received_property, "Combat", "Est en combat")
        )
        self.game_info_signals.life_point.connect(
            partial(self.on_received_property, "Combat", "Vie")
        )
        self.game_info_signals.max_life_point.connect(
            partial(self.on_received_property, "Combat", "Vie maximum")
        )
        self.game_info_signals.inventory_weight.connect(
            self.on_inventory_weight_updated
        )
        self.game_info_signals.weight_max.connect(self.on_weight_max_updated)
        self.grid_signals.new_map_id.connect(
            partial(self.on_received_property, "Map", "Map id")
        )
        self.game_info_signals.count_object_by_uid.connect(
            partial(
                self.on_received_property,
                "Inventaire",
                "Nombre d'objet dans l'inventaire",
            )
        )

    def on_inventory_weight_updated(self, inventory_weight: int):
        self.inventory_weight = inventory_weight
        self.on_received_property(
            "Inventaire", "Poids", f"{self.inventory_weight}/{self.weight_max}"
        )

    def on_weight_max_updated(self, weight_max: int):
        self.weight_max = weight_max
        self.on_received_property(
            "Inventaire", "Poids", f"{self.inventory_weight}/{self.weight_max}"
        )

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
