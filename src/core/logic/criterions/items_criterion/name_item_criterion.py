from src.core.logic.criterions.item_criterion import ItemCriterion


class NameItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        name: str = PlayedCharacterManager().infos.name
        respected = False
        criterion_value: str = str(self.criterion_value)
        if self.item_operator.text == "=":
            respected = name == criterion_value

        if self.item_operator.text == "!":
            respected = name != criterion_value

        if self.item_operator.text == "~":
            respected = name.lower() == criterion_value.lower()

        if self.item_operator.text == "S":
            respected = name.lower().index(criterion_value.lower()) == 0

        if self.item_operator.text == "s":
            respected = name.index(criterion_value) == 0

        if self.item_operator.text == "E":
            respected = name.lower().index(criterion_value.lower()) == len(name) - len(
                criterion_value
            )

        if self.item_operator.text == "e":
            respected = name.index(criterion_value) == len(name) - len(criterion_value)

        if self.item_operator.text == "v" or self.item_operator.text == "i":
            return respected

        return False

    def get_criterion(self, *args, **kwargs) -> int:
        return 0
