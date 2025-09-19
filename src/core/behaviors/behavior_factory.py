from src.core.behaviors.behavior import Behavior
from src.core.behaviors.equipment.auto_equipment_behavior import AutoEquipmentBehavior
from src.core.behaviors.interactives.fake_bad_interactive_behavior import (
    FakeBadInteractiveBehavior,
)
from src.core.behaviors.movements.fake_bad_movement_behavior import (
    FakeBadMovementBehavior,
)
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.behaviors.quests.quest_behavior import QuestBehavior
from src.core.behaviors.sale_hotel.sale_hotel_sell_behavior import (
    SaleHotelSellBehavior,
)

type Instruction = tuple[Behavior, dict[str, object]]


USABLE_BEHAVIORS: list[type[Behavior]] = [
    MuleAcceptBehavior,
    DungeonBehavior,
    QuestBehavior,
    SaleHotelSellBehavior,
    AutoEquipmentBehavior,
    FakeBadMovementBehavior,
    FakeBadInteractiveBehavior,
    QuestBehavior,
]
