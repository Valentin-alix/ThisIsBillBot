from typing import override

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.models.datas.recipe_root import RecipeItem

from src.gui.components.group_list import GroupList


class RecipeGroup(GroupList[RecipeItem]):
    def __init__(self, recipes: list[RecipeItem], **kwargs) -> None:
        super().__init__(items=recipes, is_lazy_loaded=True, **kwargs)

    @property
    def recipes(self):
        return self.items_by_name.values()

    @override
    def get_name_item(self, item: RecipeItem) -> str:
        name_id = DataReader().item_by_id[item.resultId].nameId
        return I18N().name_by_id.get(name_id, "") if name_id else ""
