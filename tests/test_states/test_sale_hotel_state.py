from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeBidHouseSearchRequest,
    ExchangeBidSellerStartedEvent,
    SellingConditions,
)

from src.core.bot.bot import Bot


class TestSaleHotelState:
    def test_exchange_bid_seller_started_sets_conditions(
        self,
        runtime_bot: Bot,
    ):
        selling_conditions = SellingConditions(max_item_per_account=15)

        msg = ExchangeBidSellerStartedEvent(selling_conditions=selling_conditions)

        runtime_bot.event_manager.process_msg(msg)

        assert runtime_bot.game_state.sale_hotel.bid_seller_condition is not None
        assert (
            runtime_bot.game_state.sale_hotel.bid_seller_condition.max_item_per_account
            == 15
        )

    def test_exchange_bid_house_search_with_follow_sets_gid(
        self,
        runtime_bot: Bot,
    ):
        msg = ExchangeBidHouseSearchRequest(
            object_gid=12345,
            follow=True,
        )

        runtime_bot.event_manager.process_msg(msg)

        assert runtime_bot.game_state.sale_hotel.current_search_item_gid == 12345

    def test_exchange_bid_house_search_without_follow_clears_gid(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.sale_hotel.current_search_item_gid = 12345

        msg = ExchangeBidHouseSearchRequest(
            object_gid=67890,
            follow=False,
        )

        runtime_bot.event_manager.process_msg(msg)

        assert runtime_bot.game_state.sale_hotel.current_search_item_gid is None
