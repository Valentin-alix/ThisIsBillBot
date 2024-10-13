import os
from threading import _RLock as RLock

import msgspec

from src.const import RESOURCE_FOLDER
from src.interfaces.metaclasses.singleton import Singleton


class SaleHotelController(metaclass=Singleton):
    _HDV_BY_UID_BY_PLAYER_LOCK = RLock()
    _HDV_BY_UID_BY_PLAYER_PATH = os.path.join(
        RESOURCE_FOLDER, "bid_seller_item_by_uid_by_player_id.json"
    )

    _AVG_PRICE_BY_GID_LOCK = RLock()
    _AVG_PRICE_BY_GID_PATH = os.path.join(RESOURCE_FOLDER, "avg_price_by_gid.json")

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
    ) -> dict[int, dict[int, tuple[int, int]]]:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            if not os.path.exists(self._HDV_BY_UID_BY_PLAYER_PATH):
                with open(self._HDV_BY_UID_BY_PLAYER_PATH, "wb+") as file:
                    file.write(msgspec.json.encode({}))
            with open(self._HDV_BY_UID_BY_PLAYER_PATH, "rb+") as file:
                content = msgspec.json.decode(
                    file.read(), type=dict[int, dict[int, tuple[int, int]]]
                )
        return content

    def update_hdv(
        self,
        player_id: int,
        gid_and_quantity_by_uid: dict[int, tuple[int, int]],
    ) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player()
            content[player_id] = gid_and_quantity_by_uid
            with open(self._HDV_BY_UID_BY_PLAYER_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def add_gid_quantity_by_uid_by_player_id(
        self, player_id: int, gid: int, quantity: int, uid: int
    ) -> None:
        with self._HDV_BY_UID_BY_PLAYER_LOCK:
            content = self.get_hdv_by_uid_by_player()
            if player_id not in content:
                content[player_id] = {}
            content[player_id][uid] = (gid, quantity)
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
