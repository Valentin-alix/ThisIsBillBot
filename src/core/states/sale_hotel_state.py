import dataclasses
import datetime


from d3_mapping.resources.protos.game.exchange_pb2 import SellingConditions
from src.core.states.state import State


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
        self.last_time_updated_prices = datetime.datetime(datetime.MINYEAR, 1, 1)
