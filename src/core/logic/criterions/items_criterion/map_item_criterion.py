from src.core.logic.criterions.item_criterion import ItemCriterion


class MapItemCriterion(ItemCriterion):

    _map_id: float

    def __init__(self, p_criterion: str):
        super().__init__(p_criterion)
        if PlayedCharacterManager().currentMap:
            self._map_id = PlayedCharacterManager().currentMap.mapId

    def get_criterion(self, *args, **kwargs) -> int:
        self._map_id = PlayedCharacterManager().currentMap.mapId
        return self._map_id
