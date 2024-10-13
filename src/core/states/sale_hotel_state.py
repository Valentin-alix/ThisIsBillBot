import dataclasses
import datetime

from protos.game.exchange_pb2 import SellingConditions, ExchangeBidSellerStartedEvent
from src.core.states.state import State

BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID: dict[
    int, dict[int, ExchangeBidSellerStartedEvent.ItemToSellInBid]
] = {}

AVERAGE_PRICE_BY_GID: dict[int, float] = {}


@dataclasses.dataclass
class SaleHotelState(State):
    last_time_updated_prices: datetime.datetime = dataclasses.field(
        init=False, default=datetime.datetime(datetime.MINYEAR, 1, 1)
    )
    bid_seller_condition: SellingConditions | None = dataclasses.field(
        init=False, default=None
    )
    current_search_item_gid: int | None = dataclasses.field(init=False, default=None)

    def clear_state(self):
        self.bid_seller_condition = None
        self.current_search_item_gid = None
