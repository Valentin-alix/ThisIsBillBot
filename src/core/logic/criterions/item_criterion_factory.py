from src.core.logic.criterions.interface_item_criterion import IItemCriterion
from src.core.logic.criterions.item_criterion import ItemCriterion

from src.core.logic.criterions.items_criterion.achievement_item_criterion import (
    AchievementItemCriterion,
)

from src.core.logic.criterions.items_criterion.area_item_criterion import (
    AreaItemCriterion,
)

from src.core.logic.criterions.items_criterion.day_item_criterion import (
    DayItemCriterion,
)

from src.core.logic.criterions.items_criterion.level_item_criterion import (
    LevelItemCriterion,
)
from src.core.logic.criterions.items_criterion.map_characters_item_criterion import (
    MapCharactersItemCriterion,
)

from src.core.logic.criterions.items_criterion.month_item_criterion import (
    MonthItemCriterion,
)

from src.core.logic.criterions.items_criterion.object_item_criterion import (
    ObjectItemCriterion,
)

from src.core.logic.criterions.items_criterion.quest_item_criterion import (
    QuestItemCriterion,
)
from src.core.logic.criterions.items_criterion.quest_objective_item_criterion import (
    QuestObjectiveItemCriterion,
)
from src.core.logic.criterions.items_criterion.static_criterion_item_criterion import (
    StaticCriterionItemCriterion,
)

from src.core.logic.criterions.items_criterion.sub_area_item_criterion import (
    SubareaItemCriterion,
)
from src.core.logic.criterions.items_criterion.subscribe_item_criterion import (
    SubscribeItemCriterion,
)


class ItemCriterionFactory:
    @staticmethod
    def create(criterion: str) -> IItemCriterion | None:
        type_criterion = criterion[0:2]

        item_criterion: IItemCriterion

        if type_criterion in [
            "Ca",
            "CA",
            "ca",
            "Cc",
            "CC",
            "cc",
            "CD",
            "Ce",
            "CE",
            "CH",
            "Ci",
            "CI",
            "ci",
            "CL",
            "CM",
            "CP",
            "Cs",
            "CS",
            "cs",
            "Ct",
            "CT",
            "Cv",
            "CV",
            "cv",
            "Cw",
            "CW",
            "cw",
        ]:
            item_criterion = ItemCriterion(criterion)
        elif type_criterion == "MK":
            item_criterion = MapCharactersItemCriterion(criterion)
        elif type_criterion == "OA":
            item_criterion = AchievementItemCriterion(criterion)
        elif type_criterion == "PB":
            item_criterion = SubareaItemCriterion(criterion)
        elif type_criterion == "PL":
            item_criterion = LevelItemCriterion(criterion)
        elif type_criterion == "PO":
            item_criterion = ObjectItemCriterion(criterion)
        elif type_criterion == "Po":
            item_criterion = AreaItemCriterion(criterion)
        elif type_criterion in ["Pz", "PZ"]:
            item_criterion = SubscribeItemCriterion(criterion)
        elif type_criterion in ["Qa", "Qc", "Qf"]:
            item_criterion = QuestItemCriterion(criterion)
        elif type_criterion == "Qo":
            item_criterion = QuestObjectiveItemCriterion(criterion)
        elif type_criterion == "Sd":
            item_criterion = DayItemCriterion(criterion)
        elif type_criterion == "SG":
            item_criterion = MonthItemCriterion(criterion)
        elif type_criterion == "Sc":
            item_criterion = StaticCriterionItemCriterion(criterion)
        elif type_criterion in ["PU"]:
            # is always respected
            item_criterion = StaticCriterionItemCriterion(criterion)
        else:
            raise ValueError(f"Invalid type criterion : {type_criterion}")

        return item_criterion
