from threading import RLock

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory

_STORAGE_REGISTRY: dict[int, "GuildChestStorage"] = {}
_REGISTRY_LOCK = RLock()


class GuildChestStorage:
    """Server-scoped, thread-safe store for guild-chest items and reservations.

    Obtain via GuildChestStorage.for_server(server_id); never construct directly.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._objects: dict[int, dict[int, ObjectItemInventory]] = {}
        self._gid_by_uid_by_tab: dict[int, dict[int, int]] = {}
        self._reservations: dict[int, dict[int, dict[str, int]]] = {}

    @classmethod
    def for_server(cls, server_id: int) -> "GuildChestStorage":
        if server_id not in _STORAGE_REGISTRY:
            with _REGISTRY_LOCK:
                if server_id not in _STORAGE_REGISTRY:
                    _STORAGE_REGISTRY[server_id] = cls()
        return _STORAGE_REGISTRY[server_id]

    # ── write operations ──────────────────────────────────────────────────────

    def set_tab_content(self, tab: int, objects: list[ObjectItemInventory]) -> None:
        with self._lock:
            self._objects[tab] = {obj.item.gid: obj for obj in objects}
            self._gid_by_uid_by_tab[tab] = {
                obj.item.uid: obj.item.gid for obj in objects
            }

    def set_item(self, tab: int, obj: ObjectItemInventory) -> None:
        with self._lock:
            self._objects.setdefault(tab, {})[obj.item.gid] = obj
            self._gid_by_uid_by_tab.setdefault(tab, {})[obj.item.uid] = obj.item.gid

    def remove_item_by_uid(self, tab: int, uid: int) -> None:
        with self._lock:
            uid_map = self._gid_by_uid_by_tab.get(tab)
            if uid_map is None or uid not in uid_map:
                raise ValueError(f"item uid={uid} not found in tab {tab}")
            gid = uid_map.pop(uid)
            self._objects.get(tab, {}).pop(gid, None)

    # ── read operations ───────────────────────────────────────────────────────

    def get_item_by_gid(self, tab: int, gid: int) -> ObjectItemInventory | None:
        with self._lock:
            return self._objects.get(tab, {}).get(gid)

    def get_all_items_by_gid(self) -> dict[int, ObjectItemInventory]:
        with self._lock:
            return {
                gid: obj
                for by_gid in self._objects.values()
                for gid, obj in by_gid.items()
            }

    def tab_exists(self, tab: int) -> bool:
        with self._lock:
            return tab in self._objects

    def get_tab_size(self, tab: int) -> int:
        with self._lock:
            return len(self._objects.get(tab, {}))

    def get_tab_for_gid(self, gid: int) -> int | None:
        with self._lock:
            return self._get_tab_for_gid_unlocked(gid)

    # ── reservation operations ────────────────────────────────────────────────

    def get_available_quantity(self, tab: int, gid: int) -> int:
        with self._lock:
            item = self._objects.get(tab, {}).get(gid)
            if item is None:
                return 0
            reserved = sum(self._reservations.get(tab, {}).get(gid, {}).values())
            return max(0, item.item.quantity - reserved)

    def reserve_quantity(
        self, tab: int, gid: int, quantity: int, bot_name: str
    ) -> None:
        with self._lock:
            bucket = self._reservations.setdefault(tab, {}).setdefault(gid, {})
            bucket[bot_name] = bucket.get(bot_name, 0) + quantity

    def release_reservation(
        self, tab: int, gid: int, quantity: int, bot_name: str
    ) -> None:
        with self._lock:
            bucket = self._reservations.get(tab, {}).get(gid)
            if bucket is None or bot_name not in bucket:
                raise KeyError(
                    f"No reservation for bot={bot_name!r} tab={tab} gid={gid}"
                )
            new_qty = max(0, bucket[bot_name] - quantity)
            if new_qty == 0:
                bucket.pop(bot_name)
            else:
                bucket[bot_name] = new_qty

    def clear_all_reservations_for_bot(self, bot_name: str) -> None:
        with self._lock:
            for tab_dict in self._reservations.values():
                for gid_dict in tab_dict.values():
                    gid_dict.pop(bot_name, None)

    def get_storage_objects_by_gid(self) -> dict[int, ObjectItemInventory]:
        with self._lock:
            result: dict[int, ObjectItemInventory] = {}
            for tab, items_by_gid in self._objects.items():
                reservations_by_gid = self._reservations.get(tab, {})
                for gid, item in items_by_gid.items():
                    reserved = sum(reservations_by_gid.get(gid, {}).values())
                    available = max(0, item.item.quantity - reserved)
                    if available <= 0:
                        continue
                    item_copy = type(item)()
                    item_copy.CopyFrom(item)
                    item_copy.item.quantity = available
                    result[gid] = item_copy
            return result

    def _get_tab_for_gid_unlocked(self, gid: int) -> int | None:
        for tab, items in self._objects.items():
            if gid in items:
                return tab
        return None
