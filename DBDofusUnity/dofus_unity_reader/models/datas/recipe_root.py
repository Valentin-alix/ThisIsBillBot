from msgspec import Struct


class RecipeItem(Struct, frozen=True, kw_only=True):
    resultId: int
    resultNameId: str
    resultTypeId: int
    resultLevel: int
    ingredientIds: list[int]
    quantities: list[int]
    jobId: int
    skillId: int

    def __hash__(self):
        return self.resultId.__hash__()


RecipeRoot = list[RecipeItem]
