import json
import os
from threading import RLock

from pydantic import BaseModel, RootModel

from src.const import RESOURCE_FOLDER
from src.interfaces.metaclasses.singleton import Singleton


class BotConfig(BaseModel):
    playtime_starts: list[str]
    playtime_ends: list[str]


class BotConfigs(RootModel):
    root: dict[str, BotConfig]


class BotConfigController(metaclass=Singleton):
    _BOT_CONFIG_LOCK = RLock()
    _BOT_CONFIG_PATH = os.path.join(RESOURCE_FOLDER, "bot_configs.json")

    def get_bot_config_by_login(self) -> dict[str, BotConfig]:
        with self._BOT_CONFIG_LOCK, open(self._BOT_CONFIG_PATH, "r+") as file:
            return BotConfigs.model_validate(json.load(file)).root

    def update_bot_config_by_login(self, bot_config: BotConfig, login: str):
        with self._BOT_CONFIG_LOCK:
            bot_config_by_login = self.get_bot_config_by_login()
            with open(self._BOT_CONFIG_PATH, "w+") as file:
                bot_config_by_login[login] = bot_config
                json.dump(BotConfigs(root=bot_config_by_login).model_dump(), file)


if __name__ == "__main__":
    tmp = BotConfigController().get_bot_config_by_login()
    print(tmp)
    BotConfigController().update_bot_config_by_login(
        bot_config=BotConfig(playtime_ends=["la"], playtime_starts=["poele"]),
        login="yolo",
    )
    tmp = BotConfigController().get_bot_config_by_login()
    print(tmp)
