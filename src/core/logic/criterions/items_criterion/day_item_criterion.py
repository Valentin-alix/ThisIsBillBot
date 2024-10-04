from datetime import datetime

from src.core.logic.criterions.item_criterion import ItemCriterion


class DayItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        date = datetime.now()
        return TimeManager().getDateFromTime(int(date.timestamp()))[2]
