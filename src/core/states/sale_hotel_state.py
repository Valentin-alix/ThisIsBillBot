import dataclasses
import datetime

from datas.protos.non_obf.game.exchange_pb2 import SellingConditions

from src import const
from src.controller.game_data import GameDataController
from src.core.config import get_time_beween_sale_hotel_prices
from src.core.signals.player_signals import GameInfoSignals
from src.core.states.player_state import PlayerState
from src.core.states.state import State


@dataclasses.dataclass
class SaleHotelState(State):
    player_state: PlayerState
    game_info_signals: GameInfoSignals
    timedelta_for_next_sale_hotel_prices: datetime.timedelta = dataclasses.field(
        init=False, default_factory=get_time_beween_sale_hotel_prices
    )
    _last_time_updated_prices: datetime.datetime = dataclasses.field(
        init=False, default=datetime.datetime(datetime.MINYEAR, 1, 1)
    )
    bid_seller_condition: SellingConditions | None = dataclasses.field(init=False, default=None)
    current_search_item_gid: int | None = dataclasses.field(init=False, default=None)
    current_search_type_id: int | None = dataclasses.field(init=False, default=None)

    def clear_state(self):
        self.bid_seller_condition = None
        self.current_search_item_gid = None

    @property
    def should_update_price(self):
        return (
            datetime.datetime.now() - self.last_time_updated_prices
            > self.timedelta_for_next_sale_hotel_prices
        )

    @property
    def last_time_updated_prices(self) -> datetime.datetime:
        return self._last_time_updated_prices

    @last_time_updated_prices.setter
    def last_time_updated_prices(self, value: datetime.datetime):
        self._last_time_updated_prices = value
        if const.DEBUG:
            self.game_info_signals.last_time_updated_prices.emit(value)

    @property
    def is_full_object_in_sale_hotel(self):
        return self.bid_seller_condition is not None and (
            len(
                GameDataController()
                .get_hdv_by_uid_by_player(self.player_state.server_id)
                .get(self.player_state.character_id, {})
            )
            >= self.bid_seller_condition.max_item_per_account
        )
