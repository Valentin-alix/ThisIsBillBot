from src.core.logic.criterions.item_criterion import ItemCriterion


class MonthItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        date: Date = Date()
        monthInt: int = TimeManager().getDateFromTime(date.getTime())[3]
        return monthInt - 1
