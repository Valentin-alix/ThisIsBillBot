import os
from threading import RLock

import msgspec
from cachetools import TTLCache, cached
from dofus_unity_reader.enums.jobs_enum import JobEnum

from src.const import RESOURCE_FOLDER
from python_utils.singleton import Singleton

TTL_CACHE: TTLCache[object, dict[int, tuple[int, int]]] = TTLCache(
    maxsize=100,
    ttl=60 * 60 * 3 * 1000,
)


class GfxMappingController(metaclass=Singleton):
    _COLLECTABLE_MAP_CHECKED_LOCK = RLock()
    _GFX_TO_ITEM_LOCK = RLock()

    _GFX_TO_ITEM_PATH = os.path.join(RESOURCE_FOLDER, "gfx_to_item.json")
    _COLLECTABLE_MAP_CHECKED_PATH = os.path.join(
        RESOURCE_FOLDER, "collectable_map_checked.json"
    )

    @cached(TTL_CACHE)
    def get_item_job_by_gfx(self) -> dict[int, tuple[int, int]]:
        with self._GFX_TO_ITEM_LOCK, open(self._GFX_TO_ITEM_PATH, "rb+") as file:
            content = msgspec.json.decode(file.read(), type=dict[int, tuple[int, int]])
        return content

    def add_multiple_item_job_by_gfx(
        self,
        item_and_job_by_gfx_array: list[tuple[int, int, JobEnum]],
    ) -> None:
        if len(item_and_job_by_gfx_array) == 0:
            return
        with self._GFX_TO_ITEM_LOCK:
            content = self.get_item_job_by_gfx()
            for item_and_job_by_gfx in item_and_job_by_gfx_array:
                gfx_id, item_id, job_id = item_and_job_by_gfx
                if gfx_id in content:
                    continue
                content[gfx_id] = (item_id, job_id)
            with open(self._GFX_TO_ITEM_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))

    def get_map_ids_checked(self) -> set[int]:
        with (
            self._COLLECTABLE_MAP_CHECKED_LOCK,
            open(self._COLLECTABLE_MAP_CHECKED_PATH, "rb+") as file,
        ):
            content = msgspec.json.decode(file.read(), type=set[int])
        return content

    def add_map_id_checked(self, map_id: int) -> None:
        with self._COLLECTABLE_MAP_CHECKED_LOCK:
            content = self.get_map_ids_checked()
            if map_id in content:
                return
            content.add(map_id)
            with open(self._COLLECTABLE_MAP_CHECKED_PATH, "wb+") as file:
                file.write(msgspec.json.encode(content))
