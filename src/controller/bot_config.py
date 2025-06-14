import json
import logging
import os
from threading import RLock
from typing import ClassVar, Literal

from ankama_launcher_emulator_premium.decrypter.hardware_identity import (
    generate_hardware_id,
)
from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfileController,
)
from ankama_launcher_emulator_premium.utils.proxy import (
    ProxyConfig,
    build_http_proxy_url,
    build_socks_proxy_url,
)
from pydantic import BaseModel, Field, RootModel
from python_utils.singleton import Singleton

from src.const import RESOURCE_FOLDER


class BotConfig(BaseModel):
    schedule_profile: str | None = None
    connection_mode: Literal["mitm", "socket"] = "socket"
    hardware_id: str = Field(default_factory=generate_hardware_id)


class BotConfigs(RootModel):
    root: dict[str, BotConfig]


logger = logging.getLogger()


class BotConfigController(metaclass=Singleton):
    use_bot_config_json: ClassVar[bool] = True
    _BOT_CONFIG_LOCK = RLock()
    _BOT_CONFIG_PATH = os.path.join(RESOURCE_FOLDER, "bot_configs.json")
    _all_configs: dict[str, BotConfig] = {}

    def get_bot_config_by_login(self) -> dict[str, BotConfig]:
        if not self.use_bot_config_json:
            return self._all_configs
        with self._BOT_CONFIG_LOCK:
            with open(self._BOT_CONFIG_PATH, "r") as file:
                return BotConfigs.model_validate(json.load(file)).root

    def _write_all_configs(self, bot_configs: dict[str, BotConfig]) -> None:
        if not self.use_bot_config_json:
            self._all_configs = bot_configs
            return
        with self._BOT_CONFIG_LOCK:
            with open(self._BOT_CONFIG_PATH, "w") as file:
                json.dump(BotConfigs(root=bot_configs).model_dump(), file, indent=2)

    def get_bot_config(self, login: str) -> BotConfig:
        with self._BOT_CONFIG_LOCK:
            bot_config_by_login = self.get_bot_config_by_login()
            bot_config = bot_config_by_login.get(login)
            if bot_config:
                return bot_config
            bot_config_by_login[login] = BotConfig()
            self._write_all_configs(bot_config_by_login)
            return bot_config_by_login[login]

    def update_bot_config_by_login(self, bot_config: BotConfig, login: str):
        with self._BOT_CONFIG_LOCK:
            all_configs = self.get_bot_config_by_login()
            all_configs[login] = bot_config
            self._write_all_configs(all_configs)

    def assign_least_used_profile(self, login: str) -> str:
        """Assign the least represented schedule profile to ``login`` and persist it.

        Balances accounts across the available profiles so new accounts auto-launch
        on a spread of playtime slots. Returns the chosen profile id.
        """
        profiles = ScheduleProfileController().get_all_profiles()
        if not profiles:
            raise ValueError("Did not found any profile")
        with self._BOT_CONFIG_LOCK:
            all_configs = self.get_bot_config_by_login()
            counts = {profile_id: 0 for profile_id in profiles}
            for config in all_configs.values():
                if config.schedule_profile:
                    counts[config.schedule_profile] += 1

            chosen = min(sorted(counts), key=lambda profile_id: counts[profile_id])
            config = all_configs.get(login, BotConfig())
            config.schedule_profile = chosen
            all_configs[login] = config
            self._write_all_configs(all_configs)
        return chosen

    def assign_profile(self, login: str, profile_id: str | None) -> str | None:
        profiles = ScheduleProfileController().get_all_profiles()
        if profile_id and profile_id not in profiles:
            raise ValueError(f"Unknown schedule profile {profile_id}")
        with self._BOT_CONFIG_LOCK:
            all_configs = self.get_bot_config_by_login()
            config = all_configs.get(login, BotConfig())
            config.schedule_profile = profile_id
            all_configs[login] = config
            self._write_all_configs(all_configs)
        return profile_id

    def assign_mode(self, login: str, mode: Literal["socket"] | Literal["mitm"]):
        with self._BOT_CONFIG_LOCK:
            all_configs = self.get_bot_config_by_login()
            config = all_configs.get(login, BotConfig())
            config.connection_mode = mode
            all_configs[login] = config
            self._write_all_configs(all_configs)

    def resolve_bot_proxy(self, config: BotConfig) -> ProxyConfig:
        if config.schedule_profile is None:
            raise ValueError("Bot config must have a schedule profile")
        profile = ScheduleProfileController().get_profile(config.schedule_profile)
        if profile is None:
            raise ValueError(f"Unknown schedule profile {config.schedule_profile}")
        return profile.proxy

    def resolve_bot_http_proxy_url(self, config: BotConfig) -> str:
        return build_http_proxy_url(self.resolve_bot_proxy(config))

    def resolve_bot_socks_proxy_url(self, config: BotConfig) -> str:
        return build_socks_proxy_url(self.resolve_bot_proxy(config))

    def remove_bot_config(self, login: str):
        with self._BOT_CONFIG_LOCK:
            all_configs = self.get_bot_config_by_login()
            all_configs.pop(login, None)
            self._write_all_configs(all_configs)
