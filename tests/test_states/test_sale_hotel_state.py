import datetime

from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    SellingConditions,
)
from tests.test_states.state_test_base import StateTestBase


class TestSaleHotelState(StateTestBase):
    def test_initial_state(self):
        assert self.game_state.sale_hotel.bid_seller_condition is None
        assert self.game_state.sale_hotel.current_search_item_gid is None
        assert self.game_state.sale_hotel.last_time_updated_prices == datetime.datetime(
            datetime.MINYEAR, 1, 1
        )

    def test_clear_state_resets_values(self):
        self.game_state.sale_hotel.bid_seller_condition = SellingConditions(
            max_item_per_account=10
        )
        self.game_state.sale_hotel.current_search_item_gid = 123
        self.game_state.sale_hotel.last_time_updated_prices = datetime.datetime.now()

        self.game_state.sale_hotel.clear_state()

        assert self.game_state.sale_hotel.bid_seller_condition is None
        assert self.game_state.sale_hotel.current_search_item_gid is None
        assert self.game_state.sale_hotel.last_time_updated_prices == datetime.datetime(
            datetime.MINYEAR, 1, 1
        )

    def test_exchange_bid_seller_started_sets_conditions(self):
        selling_conditions = SellingConditions(max_item_per_account=15)
        msg = ExchangeBidSellerStartedEvent(selling_conditions=selling_conditions)

        self.inject(msg)

        assert self.game_state.sale_hotel.bid_seller_condition is not None
        assert (
            self.game_state.sale_hotel.bid_seller_condition.max_item_per_account == 15
        )

    def test_exchange_bid_house_search_with_follow_sets_gid(self):
        msg = ExchangeBidHouseSearchRequest(object_gid=12345, follow=True)

        self.inject(msg)

        assert self.game_state.sale_hotel.current_search_item_gid == 12345

    def test_exchange_bid_house_search_without_follow_clears_gid(self):
        self.game_state.sale_hotel.current_search_item_gid = 12345

        msg = ExchangeBidHouseSearchRequest(object_gid=67890, follow=False)

        self.inject(msg)

        assert self.game_state.sale_hotel.current_search_item_gid is None

    def test_exchange_bid_price_event_received(self):
        msg = ExchangeBidPriceEvent(
            object_gid=100,
            average_price=5000,
            bid_price_for_seller=ExchangeBidPriceEvent.BidPriceForSeller(
                minimal_prices=[1000, 10000, 100000, 1000000]
            ),
        )

        self.inject(msg)

    def test_last_time_updated_prices_setter(self):
        new_time = datetime.datetime(2024, 6, 15, 12, 30)
        self.game_state.sale_hotel.last_time_updated_prices = new_time

        assert self.game_state.sale_hotel.last_time_updated_prices == new_time

    def test_is_full_object_in_sale_hotel_false_when_no_condition(self):
        self.game_state.sale_hotel.bid_seller_condition = None

        assert self.game_state.sale_hotel.is_full_object_in_sale_hotel is False

    def test_bid_seller_condition_setter(self):
        condition = SellingConditions(max_item_per_account=20)
        self.game_state.sale_hotel.bid_seller_condition = condition

        assert (
            self.game_state.sale_hotel.bid_seller_condition.max_item_per_account == 20
        )

    def test_search_toggle_follow_on_off(self):
        msg_follow_on = ExchangeBidHouseSearchRequest(object_gid=100, follow=True)
        self.inject(msg_follow_on)
        assert self.game_state.sale_hotel.current_search_item_gid == 100

        msg_follow_off = ExchangeBidHouseSearchRequest(object_gid=100, follow=False)
        self.inject(msg_follow_off)
        assert self.game_state.sale_hotel.current_search_item_gid is None

    def test_multiple_seller_started_events(self):
        msg1 = ExchangeBidSellerStartedEvent(
            selling_conditions=SellingConditions(max_item_per_account=5)
        )
        self.inject(msg1)
        assert self.game_state.sale_hotel.bid_seller_condition is not None
        assert self.game_state.sale_hotel.bid_seller_condition.max_item_per_account == 5

        msg2 = ExchangeBidSellerStartedEvent(
            selling_conditions=SellingConditions(max_item_per_account=10)
        )
        self.inject(msg2)
        assert self.game_state.sale_hotel.bid_seller_condition is not None
        assert (
            self.game_state.sale_hotel.bid_seller_condition.max_item_per_account == 10
        )

    def test_search_different_items_sequentially(self):
        msg1 = ExchangeBidHouseSearchRequest(object_gid=100, follow=True)
        self.inject(msg1)
        assert self.game_state.sale_hotel.current_search_item_gid == 100

        msg2 = ExchangeBidHouseSearchRequest(object_gid=200, follow=True)
        self.inject(msg2)
        assert self.game_state.sale_hotel.current_search_item_gid == 200

        msg3 = ExchangeBidHouseSearchRequest(object_gid=300, follow=True)
        self.inject(msg3)
        assert self.game_state.sale_hotel.current_search_item_gid == 300
