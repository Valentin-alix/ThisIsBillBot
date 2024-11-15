import dataclasses
import datetime


from d3_mapping.resources.protos.game.exchange_pb2 import SellingConditions
from src.core.states.state import State
from src.signals.player_signals import GameInfoSignals


@dataclasses.dataclass
class SaleHotelState(State):
    game_info_signals: GameInfoSignals
    _last_time_updated_prices: datetime.datetime = dataclasses.field(
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

    @property
    def last_time_updated_prices(self) -> datetime.datetime:
        return self._last_time_updated_prices

    @last_time_updated_prices.setter
    def last_time_updated_prices(self, value: datetime.datetime):
        self._last_time_updated_prices = value
        self.game_info_signals.last_time_updated_prices.emit(value)
