import json
import os
from functools import cached_property
from math import log
from pathlib import Path

from D3Database.data_center.data_reader import DataReader
from src.utils.metaclasses.singleton import Singleton

SPEED_SCORE_BY_GID_PATH = os.path.join(
    Path(__file__).parent.parent.parent, "resources", "speed_score_by_gid.json"
)


class SpeedSellScoreController(metaclass=Singleton):
    @cached_property
    def get_speed_sell_score_by_gid(self) -> dict[int, float]:
        with open(SPEED_SCORE_BY_GID_PATH, "r") as file:
            speed_score = {
                key: log(value + 2, 2) for key, value in json.load(file).items()
            }
            for item_id in DataReader().item_by_id:
                if item_id not in speed_score:
                    speed_score[item_id] = 1
            return speed_score
