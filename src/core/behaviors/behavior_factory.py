from dataclasses import dataclass, field
from typing import Any

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.fake_bad_movement_behavior import FakeBadMovementBehavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import SaleHotelPricesBehavior
from src.core.behaviors.sale_hotel.sale_hotel_scraping_behavior import SaleHotelScrapingBehavior

type Instruction = tuple[Behavior, dict[str, Any]]


@dataclass
class BehaviorFactory(Behavior):
    _instructions: list[Instruction] = field(init=False, default_factory=list)

    def run(self, instructions: list[Instruction]) -> None:
        self._instructions = instructions
        self.process_instruction()

    def process_instruction(self):
        if len(self._instructions) == 0:
            return self.finish()
        behavior, args = self._instructions.pop()
        behavior.start(**args, callback=self.process_instruction, parent=self)


USABLE_BEHAVIORS: list[type[Behavior]] = [
    MuleGiveBehavior,
    MuleAcceptBehavior,
    DungeonBehavior,
    SaleHotelPricesBehavior,
    SaleHotelScrapingBehavior,
    FakeBadMovementBehavior,
]
