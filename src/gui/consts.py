from src.core.behaviors.behavior import Behavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_scraping_behavior import (
    SaleHotelScrapingBehavior,
)

BASE_WIDTH: int = 1280
BASE_HEIGHT: int = 720

USABLE_BEHAVIORS: list[type[Behavior]] = [
    MuleGiveBehavior,
    MuleAcceptBehavior,
    DungeonBehavior,
    SaleHotelPricesBehavior,
    SaleHotelScrapingBehavior,
]
