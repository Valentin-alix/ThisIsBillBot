from data_center.data_reader import DataReader
from models.datas.recipe_root import RecipeItem
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, TransparentToolButton

from src.common.logger import Logger
from src.gui.pages.craft.recipe_group import RecipeGroup
from src.gui.pages.craft.recipe_table import RecipeTable
from src.signals.bot_signals import BotSignals


class CraftPage(QWidget):
    def __init__(self, logger: Logger, farm_signals: BotSignals):
        super().__init__()
        self.logger = logger
        self.farm_signals = farm_signals

        recipes: list[RecipeItem] = DataReader().recipes
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.setLayout(self.main_layout)

        self.play_btn = TransparentToolButton(FluentIcon.PLAY)
        self.farm_signals.play.connect(self.on_play)
        self.play_btn.clicked.connect(self.on_click_play)
        self.layout().addWidget(self.play_btn)

        self.stop_btn = TransparentToolButton(FluentIcon.PAUSE)
        self.farm_signals.stop.connect(self.on_stop)
        self.stop_btn.clicked.connect(self.on_click_stop)
        self.layout().addWidget(self.stop_btn)
        self.stop_btn.hide()

        self.craft_table = RecipeTable(recipes=[])
        self.craft_group = RecipeGroup(recipes=recipes)

        self.craft_group.signals.clicked_elem_queue.connect(self.on_added_recipe_queue)
        self.craft_table.signals.removed_recipe.connect(self.on_removed_recipe_queue)

        self.layout().addWidget(self.craft_table)
        self.layout().addWidget(self.craft_group)

    @pyqtSlot(object)
    def on_removed_recipe_queue(self, recipe: RecipeItem):
        self.craft_group.add_item(recipe)

    @pyqtSlot(object)
    def on_added_recipe_queue(self, recipe: RecipeItem):
        self.craft_group.remove_item(recipe)
        self.craft_table.add_recipe(recipe)
        self.logger.info(f"Added recipe for result {recipe.resultId}")

    @pyqtSlot()
    def on_play(self):
        self.stop_btn.show()
        self.play_btn.hide()

    @pyqtSlot()
    def on_click_play(self):
        recipes = self.craft_table.recipes
        self.farm_signals.play_crafter.emit(recipes)

    @pyqtSlot()
    def on_click_stop(self):
        self.farm_signals.stop.emit()

    @pyqtSlot()
    def on_stop(self):
        self.play_btn.show()
        self.stop_btn.hide()
