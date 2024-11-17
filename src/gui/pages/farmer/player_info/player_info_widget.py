from functools import partial
from typing import Any

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea

from src.core.bot.bot import Bot
from src.gui.pages.farmer.player_info.property_group_widget import PropertyGroupWidget


class PlayerInfoWidget(QWidget):
    def __init__(self, bot: Bot):
        super().__init__()

        self.bot = bot

        scroll_area = SingleDirectionScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container_widget = QWidget()
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        v_layout.setContentsMargins(0, 0, 0, 0)
        container_widget.setLayout(v_layout)

        scroll_area.setWidget(container_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.inventory_weight: int = 0
        self.weight_max: int = 0

        self.group_by_key: dict[str, PropertyGroupWidget] = {}
        self._pending_updates: dict[tuple[str, str], Any] = {}
        self._update_scheduled = False

        self.bot.game_info_signals.character_id.connect(
            partial(self.on_received_property, "Joueur", "Player id")
        )
        self.bot.game_info_signals.character_name.connect(
            partial(self.on_received_property, "Joueur", "Nom")
        )
        self.bot.game_info_signals.breed_id.connect(
            partial(self.on_received_property, "Joueur", "Race id")
        )
        self.bot.game_info_signals.level.connect(
            partial(self.on_received_property, "Joueur", "Niveau")
        )
        self.bot.game_info_signals.server_id.connect(
            partial(self.on_received_property, "Joueur", "Serveur id")
        )
        self.bot.game_info_signals.has_guild.connect(
            partial(self.on_received_property, "Joueur", "A une guilde")
        )
        self.bot.game_info_signals.subscription_end_date.connect(
            partial(self.on_received_property, "Joueur", "Date de fin d'abonnement")
        )
        self.bot.game_info_signals.in_fight.connect(
            partial(self.on_received_property, "Combat", "Est en combat")
        )
        self.bot.game_info_signals.is_our_turn.connect(
            partial(self.on_received_property, "Combat", "Notre tour")
        )
        self.bot.game_info_signals.life_point.connect(
            partial(self.on_received_property, "Combat", "Vie")
        )
        self.bot.game_info_signals.max_life_point.connect(
            partial(self.on_received_property, "Combat", "Vie maximum")
        )
        self.bot.inventory_signals.inventory_weight.connect(
            self.on_inventory_weight_updated
        )
        self.bot.inventory_signals.weight_max.connect(self.on_weight_max_updated)
        self.bot.grid_signals.new_map_id.connect(
            partial(self.on_received_property, "Map", "Map id")
        )
        self.bot.grid_signals.is_in_map_transition.connect(
            partial(self.on_received_property, "Map", "Est en transition de map")
        )
        self.bot.game_info_signals.is_in_haven_bag.connect(
            partial(self.on_received_property, "Map", "Dans le havre-sac")
        )
        self.bot.inventory_signals.kamas.connect(
            partial(self.on_received_property, "Inventaire", "Kamas")
        )
        self.bot.game_info_signals.tab_number.connect(
            partial(self.on_received_property, "Coffre de guilde", "Onglet actuel")
        )
        self.bot.game_info_signals.last_time_updated_prices.connect(
            partial(self.on_received_property, "Hotel de vente", "Derniere maj prix")
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
        self._pending_updates[(group_key, key)] = value
        if not self._update_scheduled:
            self._update_scheduled = True
            QTimer.singleShot(0, self._flush_updates)

    def _flush_updates(self):
        for (group_key, key), value in self._pending_updates.items():
            group_widget = self.get_or_create_group_widget(group_key)
            group_widget.add_or_update_property_label(key, str(value))
        self._pending_updates.clear()
        self._update_scheduled = False

    def get_or_create_group_widget(self, group_key: str) -> PropertyGroupWidget:
        group_widget = self.group_by_key.get(group_key)
        if group_widget is not None:
            return group_widget

        group_widget = PropertyGroupWidget(key=group_key)
        self.group_by_key[group_key] = group_widget
        self.layout().addWidget(group_widget)

        return group_widget
