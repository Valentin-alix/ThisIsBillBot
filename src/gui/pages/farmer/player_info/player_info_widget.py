from functools import partial

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
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
        self.bot.game_info_signals.server_id.connect(self.on_server_id_changed)
        self.bot.game_info_signals.has_guild.connect(
            partial(self.on_received_property, "Joueur", "A une guilde")
        )
        self.bot.game_info_signals.tab_number.connect(
            partial(self.on_received_property, "Coffre de guilde", "Onglet actuel")
        )
        self.bot.game_info_signals.last_time_updated_prices.connect(
            partial(self.on_received_property, "Hotel de vente", "Derniere maj prix")
        )

    @pyqtSlot(int)
    def on_server_id_changed(self, server_id: int) -> None:
        server = DataReader().server_by_id[server_id]
        server_name = I18N().name_by_id[server.nameId]
        self.on_received_property("Joueur", "Serveur", server_name)
