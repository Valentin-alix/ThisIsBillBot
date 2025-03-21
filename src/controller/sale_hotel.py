import os
from collections import defaultdict
from threading import _RLock as RLock

import msgspec
from cachetools import TTLCache, cached
from python_utils.singleton import Singleton

from src.const import RESOURCE_FOLDER

SALE_HOTEL_FOLDER = os.path.join(RESOURCE_FOLDER, "sale_hotel")

AVG_PRICE_CACHE = TTLCache[int, dict[int, float]](maxsize=100, ttl=60 * 60 * 3 * 1000)


class SaleHotelController(metaclass=Singleton):
    _HDV_BY_UID_BY_PLAYER_LOCK = RLock()
    _AVG_PRICE_BY_GID_LOCK = RLock()

    def _get_server_folder(self, server_id: int) -> str:
        folder = os.path.join(SALE_HOTEL_FOLDER, f"server_{server_id}")
        os.makedirs(folder, exist_ok=True)
        return folder

    def _get_avg_price_path(self, server_id: int) -> str:
        return os.path.join(self._get_server_folder(server_id), "avg_price_by_gid.json")

    def _get_hdv_path(self, server_id: int) -> str:
        return os.path.join(
            self._get_server_folder(server_id),
            "bid_seller_item_by_uid_by_player_id.json",
        )

    @cached(AVG_PRICE_CACHE)
    def get_avg_price_by_gid(self, server_id: int) -> dict[int, float]:
        path = self._get_avg_price_path(server_id)
        if not os.path.exists(path):
            with open(path, "wb+") as file:
                file.write(msgspec.json.encode({}))
        with (
            self._AVG_PRICE_BY_GID_LOCK,
            open(path, "rb+") as file,
        ):
            content = msgspec.json.decode(file.read(), type=dict[int, float])
        return content

    def add_multiple_avg_price_by_gid(
        self,
        server_id: int,
        avg_price_gid_array: list[tuple[int, int]],
    ) -> None:
        if len(avg_price_gid_array) == 0:
            return
        with self._AVG_PRICE_BY_GID_LOCK:
            content = self.get_avg_price_by_gid(server_id)
            for avg_price, gid in avg_price_gid_array:
                if avg_price == 0:
                    continue
                content[gid] = avg_price
            path = self._get_avg_price_path(server_id)
            with open(path, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def get_hdv_by_uid_by_player(
        self,
        server_id: int,
    ) -> dict[int, dict[int, tuple[int, int, int]]]:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            path = self._get_hdv_path(server_id)
            if not os.path.exists(path):
                with open(path, "wb+") as file:
                    file.write(msgspec.json.encode({}))
            with open(path, "rb+") as file:
                content = msgspec.json.decode(
                    file.read(), type=dict[int, dict[int, tuple[int, int, int]]]
                )
        return content

    def get_minimal_price_by_gid_and_quantity(
        self, server_id: int
    ) -> dict[tuple[int, int], int]:
        minimal_price_by_gid_and_quantity: dict[tuple[int, int], int] = {}
        hdv_players = self.get_hdv_by_uid_by_player(server_id).values()
        for gid_and_quantity_and_price_by_uid in hdv_players:
            for gid, quantity, price in gid_and_quantity_and_price_by_uid.values():
                _curr_minimal_price = minimal_price_by_gid_and_quantity.get(
                    (gid, quantity)
                )
                if _curr_minimal_price is None or _curr_minimal_price > price:
                    minimal_price_by_gid_and_quantity[(gid, quantity)] = price
        return minimal_price_by_gid_and_quantity

    def get_item_sell_quantity_by_gid(self, server_id: int):
        item_sell_quantity_by_gid: dict[int, int] = defaultdict(int)
        for quantity_by_uid in self.get_hdv_by_uid_by_player(server_id).values():
            for gid, quantity, _ in quantity_by_uid.values():
                item_sell_quantity_by_gid[gid] += quantity
        return item_sell_quantity_by_gid

    def update_hdv(
        self,
        server_id: int,
        player_id: int,
        gid_and_quantity_and_price_by_uid: dict[int, tuple[int, int, int]],
    ) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player(server_id)
            content[player_id] = gid_and_quantity_and_price_by_uid
            path = self._get_hdv_path(server_id)
            with open(path, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def add_gid_quantity_by_uid_by_player_id(
        self,
        server_id: int,
        player_id: int,
        gid: int,
        quantity: int,
        price: int,
        uid: int,
    ) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player(server_id)
            if player_id not in content:
                content[player_id] = {}
            content[player_id][uid] = (gid, quantity, price)
            path = self._get_hdv_path(server_id)
            with open(path, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def remove_uid_for_player_id(
        self, server_id: int, player_id: int, uid: int
    ) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player(server_id)
            if player_id not in content:
                content[player_id] = {}
            content[player_id].pop(uid, None)
            path = self._get_hdv_path(server_id)
            with open(path, "wb+") as file:
                file.write(msgspec.json.encode(content))
