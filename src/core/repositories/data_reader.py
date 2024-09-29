from dataclasses import dataclass, field
import os
from src.consts import DOFUS_DATA_PATH, USEFUL_DATAS_JSON
from src.interfaces.dicts.gen_datas.ItemsRoot import Data as ItemsRootData
import orjson

from src.utils import Singleton


@dataclass
class DataReader(metaclass=Singleton):
    item_by_id: dict[int, ItemsRootData] = field(init=False, default_factory=lambda: {})

    def __post_init__(self) -> None:
        with open(
            os.path.join(DOFUS_DATA_PATH, USEFUL_DATAS_JSON["Items"]), "rb"
        ) as file:
            data = orjson.loads(file.read())
        self.item_by_id = {
            ref_id["data"]["id"]: ref_id["data"]
            for ref_id in data["references"]["RefIds"]
            if "id" in ref_id["data"]
        }
