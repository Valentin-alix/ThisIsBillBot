import os
from threading import Lock

import msgspec

from src.const import RESOURCE_FOLDER
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.interfaces.enums.job_enum import JobEnum

COLLECTABLE_MAP_CHECKED_LOCK = Lock()
GFX_TO_ITEM_LOCK = Lock()


GFX_TO_ITEM_PATH = os.path.join(RESOURCE_FOLDER, "gfx_to_item.json")
COLLECTABLE_MAP_CHECKED_PATH = os.path.join(
    RESOURCE_FOLDER, "collectable_map_checked.json"
)


GFX_TO_ITEM_AND_JOB: dict[int, tuple[int, JobEnum]] | None = None
COLLECTABLE_MAP_CHECKED: set[int] | None = None


def get_gfx_to_item_and_job() -> dict[int, tuple[int, JobEnum]]:
    if GFX_TO_ITEM_AND_JOB is not None:
        return GFX_TO_ITEM_AND_JOB
    with open(GFX_TO_ITEM_PATH, "rb+") as file:
        content = msgspec.json.decode(file.read(), type=dict[int, tuple[int, JobEnum]])
    return content


def add_item_and_job_by_gfx_array(
    item_and_job_by_gfx_array: list[tuple[int, int, JobEnum]]
) -> None:
    if len(item_and_job_by_gfx_array) == 0:
        return
    with GFX_TO_ITEM_LOCK:
        content = get_gfx_to_item_and_job()
        for item_and_job_by_gfx in item_and_job_by_gfx_array:
            gfx_id, item_id, job_id = item_and_job_by_gfx
            if gfx_id in content:
                continue
            content[gfx_id] = (item_id, job_id)
        with open(GFX_TO_ITEM_PATH, "wb+") as file:
            file.write(msgspec.json.encode(content))


def get_collectable_map_checked() -> set[int]:
    if COLLECTABLE_MAP_CHECKED is not None:
        return COLLECTABLE_MAP_CHECKED
    with open(COLLECTABLE_MAP_CHECKED_PATH, "rb+") as file:
        content = msgspec.json.decode(file.read(), type=set[int])
    return content


def add_collectable_map_checked(map_id: int):
    with COLLECTABLE_MAP_CHECKED_LOCK:
        content = get_collectable_map_checked()
        if map_id in content:
            return
        content.add(map_id)
        with open(COLLECTABLE_MAP_CHECKED_PATH, "wb+") as file:
            file.write(msgspec.json.encode(content))


if __name__ == "__main__":
    for gfx, (item_id, job_id) in get_gfx_to_item_and_job().items():
        item = DataReader().item_by_id[item_id]
        print(I18N().name_by_id[item.nameId])
