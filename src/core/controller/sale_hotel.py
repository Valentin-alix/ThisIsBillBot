import os
from threading import _RLock as RLock

import msgspec

from src.const import RESOURCE_FOLDER
from src.interfaces.metaclasses.singleton import Singleton


class SaleHotelController(metaclass=Singleton):
    _BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_LOCK = RLock()
    _BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_PATH = os.path.join(
        RESOURCE_FOLDER, "bid_seller_item_by_uid_by_player_id.json"
    )

    _AVG_PRICE_BY_GID_BY_SERVER_LOCK = RLock()
    _AVG_PRICE_BY_GID_BY_SERVER_PATH = os.path.join(
        RESOURCE_FOLDER, "avg_price_by_gid_by_server.json"
    )

    def get_avg_price_by_gid_by_server(self) -> dict[int, dict[int, float]]:
        with (
            self._AVG_PRICE_BY_GID_BY_SERVER_LOCK,
            open(self._AVG_PRICE_BY_GID_BY_SERVER_PATH, "rb+") as file,
        ):
            content = msgspec.json.decode(file.read(), type=dict[int, dict[int, float]])
        return content

    def add_multiple_avg_price_by_gid_by_server(
        self,
        avg_price_gid_server_array: list[tuple[int, int, int]],
    ) -> None:
        if len(avg_price_gid_server_array) == 0:
            return
        with self._AVG_PRICE_BY_GID_BY_SERVER_LOCK:
            content = self.get_avg_price_by_gid_by_server()
            for avg_price, gid, server_id in avg_price_gid_server_array:
                if avg_price == 0:
                    continue
                if server_id not in content:
                    content[server_id] = {}
                content[server_id][gid] = avg_price
            with open(self._AVG_PRICE_BY_GID_BY_SERVER_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def get_bid_seller_gid_quantity_by_uid_by_player_id(
        self,
    ) -> dict[int, dict[int, tuple[int, int]]]:
        with (
            self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_LOCK,
            open(self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_PATH, "rb+") as file,
        ):
            content = msgspec.json.decode(
                file.read(), type=dict[int, dict[int, tuple[int, int]]]
            )
        return content

    def update_gid_quantity_by_uid_by_player_id(
        self, player_id: int, gid_and_quantity_by_uid: dict[int, tuple[int, int]]
    ) -> None:
        with self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_LOCK:
            content = self.get_bid_seller_gid_quantity_by_uid_by_player_id()
            content[player_id] = gid_and_quantity_by_uid
            with open(self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def add_gid_quantity_by_uid_by_player_id(
        self, gid: int, quantity: int, uid: int, player_id: int
    ) -> None:
        with self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_LOCK:
            content = self.get_bid_seller_gid_quantity_by_uid_by_player_id()
            if player_id not in content:
                content[player_id] = {}
            content[player_id][uid] = (gid, quantity)
            with open(self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def remove_uid_for_player_id(self, uid: int, player_id: int) -> None:
        with self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_LOCK:
            content = self.get_bid_seller_gid_quantity_by_uid_by_player_id()
            if player_id not in content:
                content[player_id] = {}
            content[player_id].pop(uid, None)
            with open(self._BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))
