from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode

from src.core.bot.bot import Bot
from src.gui.pages.farmer.player_info.player_info_widget import PlayerInfoWidget


class PlayerTab(QWidget):
    def __init__(self, bot: Bot):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        scroll_area_info = SingleDirectionScrollArea()

        player_info_widget = PlayerInfoWidget(bot)

        scroll_area_info.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area_info.setWidgetResizable(True)
        scroll_area_info.setWidget(player_info_widget)
        scroll_area_info.enableTransparentBackground()

        layout.addWidget(scroll_area_info)
