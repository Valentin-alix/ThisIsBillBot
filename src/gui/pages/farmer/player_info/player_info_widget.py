from functools import partial

from PyQt6.QtWidgets import QWidget

from src.core.bot.bot import Bot
from src.gui.pages.farmer.player_info.property_panel_widget import PropertyPanelWidget


class PlayerInfoWidget(PropertyPanelWidget):
    def __init__(self, bot: Bot, parent: QWidget | None = None):
        super().__init__(parent=parent)

        self.bot = bot

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
        self.bot.game_info_signals.tab_number.connect(
            partial(self.on_received_property, "Coffre de guilde", "Onglet actuel")
        )
        self.bot.game_info_signals.last_time_updated_prices.connect(
            partial(self.on_received_property, "Hotel de vente", "Derniere maj prix")
        )
