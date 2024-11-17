import json
import os
from threading import RLock

from pydantic import BaseModel, RootModel

from src.const import RESOURCE_FOLDER
from src.utils.metaclasses.singleton import Singleton


class BotConfig(BaseModel):
    network_interface: str | None = None
    pc_id: int = int(os.environ.get("PC_ID", 2))
    schedule_profile: str | None = None


class BotConfigs(RootModel):
    root: dict[str, BotConfig]


class BotConfigController(metaclass=Singleton):
    _BOT_CONFIG_LOCK = RLock()
    _BOT_CONFIG_PATH = os.path.join(RESOURCE_FOLDER, "bot_configs.json")

    def _get_all_configs(self) -> dict[str, BotConfig]:
        with open(self._BOT_CONFIG_PATH, "r") as file:
            return BotConfigs.model_validate(json.load(file)).root

    def get_bot_config_by_login(self) -> dict[str, BotConfig]:
        with self._BOT_CONFIG_LOCK:
            return {
                key: value
                for key, value in self._get_all_configs().items()
                if value.pc_id == int(os.environ.get("PC_ID", -1))
            }

    def update_bot_config_by_login(self, bot_config: BotConfig, login: str):
        with self._BOT_CONFIG_LOCK:
            all_configs = self._get_all_configs()
            all_configs[login] = bot_config
            with open(self._BOT_CONFIG_PATH, "w") as file:
                json.dump(BotConfigs(root=all_configs).model_dump(), file, indent=2)
