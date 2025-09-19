from dataclasses import dataclass

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N

from src.core.states.game_state import GameState


@dataclass(frozen=True)
class LoadItemInfo:
    item_gid: int
    remaining_quantity: int
    tab: int

    def __str__(self) -> str:
        name_id = DataReader().item_by_id[self.item_gid].nameId
        name = I18N().name_by_id.get(name_id, f"Unknown {self.item_gid}")
        return f"{name} : {self.remaining_quantity}"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class PendingLoadItem:
    item_gid: int
    remaining_quantity: int
    tab: int

    @classmethod
    def from_request(cls, request: LoadItemInfo) -> "PendingLoadItem":
        return cls(
            item_gid=request.item_gid,
            remaining_quantity=request.remaining_quantity,
            tab=request.tab,
        )

    def to_request(self) -> LoadItemInfo:
        return LoadItemInfo(
            item_gid=self.item_gid,
            remaining_quantity=self.remaining_quantity,
            tab=self.tab,
        )


def get_portable_quantity(game_state: GameState, item_gid: int) -> int:
    return (game_state.inventory.weight_max - game_state.inventory.inventory_weight) // (
        DataReader().item_by_id[item_gid].realWeight or 1
    )


def get_owned_quantity(game_state: GameState, item_gid: int) -> int:
    return sum(
        object_item.item.quantity
        for object_item in game_state.inventory.objects_by_uid.values()
        if object_item.item.gid == item_gid
    )
