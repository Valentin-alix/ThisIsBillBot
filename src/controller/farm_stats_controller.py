import os
from dataclasses import dataclass, field
from threading import RLock

import msgspec

from D3Database.utils import Singleton
from src.const import RESOURCE_FOLDER


@dataclass
class FarmStatBot:
    resources_harvested_by_name: dict[str, int] = field(default_factory=dict)
    total_fights: int = field(default_factory=int)


type FarmStatByCharacterName = dict[str, FarmStatBot]


class FarmStatsController(metaclass=Singleton):
    _STATS_LOCK = RLock()
    _STATS_PATH = os.path.join(RESOURCE_FOLDER, "farm_stats.json")

    def __init__(self):
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self._STATS_PATH):
            default_stats: FarmStatByCharacterName = {}
            with open(self._STATS_PATH, "wb+") as file:
                file.write(msgspec.json.encode(default_stats))

    def get_all_stats(self) -> FarmStatByCharacterName:
        with self._STATS_LOCK:
            self._ensure_file_exists()
            with open(self._STATS_PATH, "rb") as file:
                content = msgspec.json.decode(file.read())
                result: FarmStatByCharacterName = {}
                for character_name, stats_data in content.items():
                    result[character_name] = FarmStatBot(
                        resources_harvested_by_name=stats_data.get(
                            "resources_harvested_by_name", {}
                        ),
                        total_fights=stats_data.get("total_fights", 0),
                    )
                return result

    def get_stats(self, character_name: str) -> FarmStatBot:
        with self._STATS_LOCK:
            all_stats = self.get_all_stats()
            return all_stats.get(
                character_name,
                FarmStatBot(resources_harvested_by_name={}, total_fights=0),
            )

    def _save_stats(self, stats: FarmStatByCharacterName):
        with open(self._STATS_PATH, "wb") as file:
            file.write(msgspec.json.encode(stats))

    def add_harvested_resource(
        self, character_name: str, resource_name: str, quantity: int
    ):
        with self._STATS_LOCK:
            all_stats = self.get_all_stats()
            if character_name not in all_stats:
                all_stats[character_name] = FarmStatBot(
                    resources_harvested_by_name={}, total_fights=0
                )
            current_quantity = all_stats[
                character_name
            ].resources_harvested_by_name.get(resource_name, 0)
            all_stats[character_name].resources_harvested_by_name[resource_name] = (
                current_quantity + quantity
            )
            self._save_stats(all_stats)

    def add_fights(self, character_name: str, count: int):
        with self._STATS_LOCK:
            all_stats = self.get_all_stats()
            if character_name not in all_stats:
                all_stats[character_name] = FarmStatBot(
                    resources_harvested_by_name={}, total_fights=0
                )
            all_stats[character_name].total_fights += count
            self._save_stats(all_stats)

    def reset_stats(self, character_name: str):
        with self._STATS_LOCK:
            all_stats = self.get_all_stats()
            all_stats[character_name] = FarmStatBot(
                resources_harvested_by_name={}, total_fights=0
            )
            self._save_stats(all_stats)

    def reset_all_stats(self):
        with self._STATS_LOCK:
            self._save_stats({})
