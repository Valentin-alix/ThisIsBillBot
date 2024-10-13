from typing import override

from models.datas.recipe_root import RecipeItem
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from src.gui.components.group_list import GroupList


class RecipeGroup(GroupList[RecipeItem]):
    def __init__(self, recipes: list[RecipeItem]) -> None:
        super().__init__(items=recipes, is_lazy_loaded=True)

    @property
    def recipes(self):
        return self.items_by_name.values()

    @override
    def get_name_item(self, item: RecipeItem) -> str:
        name_id = DataReader().item_by_id[item.resultId].nameId
        return I18N.name_by_id[name_id] if name_id else ""
