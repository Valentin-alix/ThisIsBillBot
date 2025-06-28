from functools import partial

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from PyQt6.QtCore import pyqtSlot
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
        self.bot.game_info_signals.breed_id.connect(self.on_breed_id_changed)
        self.bot.game_info_signals.server_id.connect(
            partial(self.on_received_property, "Joueur", "Serveur id")
        )
        self.bot.game_info_signals.has_guild.connect(
            partial(self.on_received_property, "Joueur", "A une guilde")
        )
        self.bot.game_info_signals.tab_number.connect(
            partial(self.on_received_property, "Coffre de guilde", "Onglet actuel")
        )
        self.bot.game_info_signals.last_time_updated_prices.connect(
            partial(self.on_received_property, "Hotel de vente", "Derniere maj prix")
        )

        if self.bot.is_ready_to_play_event.is_set():
            self.on_breed_id_changed(self.bot.game_state.fight.breed_id)

    @pyqtSlot(int)
    def on_breed_id_changed(self, breed_id: int) -> None:
        if breed_id == 0:
            return
        breed = DataReader().breed_by_id[breed_id]
        breed_name = I18N().name_by_id[int(breed.shortNameId)]
        self.on_received_property("Joueur", "Classe", breed_name)
