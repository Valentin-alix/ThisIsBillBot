import os
from collections import defaultdict
from threading import _RLock as RLock
from time import perf_counter

import msgspec
from cachetools import TTLCache, cached

from src.const import RESOURCE_FOLDER
from src.interfaces.metaclasses.singleton import Singleton

TTL_CACHE = TTLCache(maxsize=100, ttl=60 * 60 * 3 * 1000)


class SaleHotelController(metaclass=Singleton):
    _HDV_BY_UID_BY_PLAYER_LOCK = RLock()
    _HDV_BY_UID_BY_PLAYER_PATH = os.path.join(
        RESOURCE_FOLDER, "bid_seller_item_by_uid_by_player_id.json"
    )

    _AVG_PRICE_BY_GID_LOCK = RLock()
    _AVG_PRICE_BY_GID_PATH = os.path.join(RESOURCE_FOLDER, "avg_price_by_gid.json")

    @cached(TTL_CACHE)
    def get_avg_price_by_gid(self) -> dict[int, float]:
        if not os.path.exists(self._AVG_PRICE_BY_GID_PATH):
            with open(self._AVG_PRICE_BY_GID_PATH, "wb+") as file:
                file.write(msgspec.json.encode({}))
        with (
            self._AVG_PRICE_BY_GID_LOCK,
            open(self._AVG_PRICE_BY_GID_PATH, "rb+") as file,
        ):
            content = msgspec.json.decode(file.read(), type=dict[int, float])
        return content

    def add_multiple_avg_price_by_gid(
        self,
        avg_price_gid_array: list[tuple[int, int]],
    ) -> None:
        if len(avg_price_gid_array) == 0:
            return
        with self._AVG_PRICE_BY_GID_LOCK:
            content = self.get_avg_price_by_gid()
            for avg_price, gid in avg_price_gid_array:
                if avg_price == 0:
                    continue
                content[gid] = avg_price
            with open(self._AVG_PRICE_BY_GID_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def get_hdv_by_uid_by_player(
        self,
    ) -> dict[int, dict[int, tuple[int, int, int]]]:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            if not os.path.exists(self._HDV_BY_UID_BY_PLAYER_PATH):
                with open(self._HDV_BY_UID_BY_PLAYER_PATH, "wb+") as file:
                    file.write(msgspec.json.encode({}))
            with open(self._HDV_BY_UID_BY_PLAYER_PATH, "rb+") as file:
                content = msgspec.json.decode(
                    file.read(), type=dict[int, dict[int, tuple[int, int, int]]]
                )
        return content

    def get_minimal_price_by_gid_and_quantity(self) -> dict[tuple[int, int], int]:
        minimal_price_by_gid_and_quantity: dict[tuple[int, int], int] = {}
        hdv_players = self.get_hdv_by_uid_by_player().values()
        for gid_and_quantity_and_price_by_uid in hdv_players:
            for gid, quantity, price in gid_and_quantity_and_price_by_uid.values():
                _curr_minimal_price = minimal_price_by_gid_and_quantity.get(
                    (gid, quantity)
                )
                if _curr_minimal_price is None or _curr_minimal_price > price:
                    minimal_price_by_gid_and_quantity[(gid, quantity)] = price
        return minimal_price_by_gid_and_quantity

    def get_item_sell_quantity_by_gid(self):
        # get sum quantity of item already in sale hotel by gid
        item_sell_quantity_by_gid: dict[int, int] = defaultdict(int)
        for quantity_by_uid in self.get_hdv_by_uid_by_player().values():
            for gid, quantity, _ in quantity_by_uid.values():
                item_sell_quantity_by_gid[gid] += quantity
        return item_sell_quantity_by_gid

    def update_hdv(
        self,
        player_id: int,
        gid_and_quantity_and_price_by_uid: dict[int, tuple[int, int, int]],
    ) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player()
            content[player_id] = gid_and_quantity_and_price_by_uid
            with open(self._HDV_BY_UID_BY_PLAYER_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def add_gid_quantity_by_uid_by_player_id(
        self, player_id: int, gid: int, quantity: int, price: int, uid: int
    ) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player()
            if player_id not in content:
                content[player_id] = {}
            content[player_id][uid] = (gid, quantity, price)
            with open(self._HDV_BY_UID_BY_PLAYER_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def remove_uid_for_player_id(self, player_id: int, uid: int) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player()
            if player_id not in content:
                content[player_id] = {}
            content[player_id].pop(uid, None)
            with open(self._HDV_BY_UID_BY_PLAYER_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))


if __name__ == "__main__":
    before = perf_counter()
    SaleHotelController().get_minimal_price_by_gid_and_quantity()
    print(perf_counter() - before)
