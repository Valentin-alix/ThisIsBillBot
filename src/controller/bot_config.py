import json
import logging
import os
from threading import RLock
from typing import ClassVar, Literal

from ankama_launcher_emulator_premium.decrypter.hardware_identity import (
    generate_hardware_id,
)
from consts import PC_ID
from pydantic import BaseModel, RootModel
from python_utils.singleton import Singleton

from src.const import RESOURCE_FOLDER
from src.controller.schedule_profile_controller import ScheduleProfileController
from src.exceptions import UnavailableNetworkInterface


class BotConfig(BaseModel):
    pc_id: int = PC_ID
    schedule_profile: str | None = None
    connection_mode: Literal["mitm", "socket"] = "socket"
    hardware_id: str | None = None


class BotConfigs(RootModel):
    root: dict[str, BotConfig]


logger = logging.getLogger()


class BotConfigController(metaclass=Singleton):
    use_bot_config_json: ClassVar[bool] = True
    _BOT_CONFIG_LOCK = RLock()
    _BOT_CONFIG_PATH = os.path.join(RESOURCE_FOLDER, "bot_configs.json")
    _all_configs: dict[str, BotConfig] = {}

    def _get_all_configs(self) -> dict[str, BotConfig]:
        with open(self._BOT_CONFIG_PATH, "r") as file:
            return BotConfigs.model_validate(json.load(file)).root

    def _write_all_configs(self, bot_configs: dict[str, BotConfig]) -> None:
        with open(self._BOT_CONFIG_PATH, "w") as file:
            json.dump(BotConfigs(root=bot_configs).model_dump(), file, indent=2)

    def get_bot_config_by_login(self) -> dict[str, BotConfig]:
        if not self.use_bot_config_json:
            return self._all_configs
        with self._BOT_CONFIG_LOCK:
            return {
                key: value
                for key, value in self._get_all_configs().items()
                if value.pc_id == PC_ID
            }

    def update_bot_config_by_login(self, bot_config: BotConfig, login: str):
        if not self.use_bot_config_json:
            logger.info(f"Assigning {bot_config} for {login}")
            self._all_configs[login] = bot_config
            return
        with self._BOT_CONFIG_LOCK:
            all_configs = self._get_all_configs()
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
            all_configs = self._get_all_configs()
            counts = {profile_id: 0 for profile_id in profiles}
            for config in all_configs.values():
                if config.pc_id == PC_ID and config.schedule_profile in counts:
                    counts[config.schedule_profile] += 1
            chosen = min(sorted(counts), key=lambda profile_id: counts[profile_id])
            existing = all_configs.get(login, BotConfig())
            all_configs[login] = existing.model_copy(
                update={"schedule_profile": chosen}
            )
            self._write_all_configs(all_configs)
        return chosen

    def resolve_bot_network_interface(
        self, config: BotConfig | None, available_interfaces: list[str]
    ) -> str | None:
        if config is None:
            return None
        return self.resolve_profile_network_interface(
            config.schedule_profile, available_interfaces
        )

    def resolve_profile_network_interface(
        self, profile_id: str | None, available_interfaces: list[str]
    ) -> str | None:
        if profile_id is None:
            return None
        profile = ScheduleProfileController().get_profile(profile_id)
        if profile is None or profile.network_interface_index is None:
            return None
        interface_index = profile.network_interface_index
        if interface_index < 1 or interface_index > len(available_interfaces):
            msg = (
                f"Profile {profile_id} requires network interface index "
                f"{interface_index}, but only {len(available_interfaces)} "
                "interfaces are available"
            )
            logger.error(msg)
            raise UnavailableNetworkInterface(msg)
        return available_interfaces[interface_index - 1]

    def get_or_create_hardware_id(self, login: str) -> str:
        with self._BOT_CONFIG_LOCK:
            all_configs = self._get_all_configs()
            bot_config = all_configs.get(login, BotConfig())
            if bot_config.hardware_id is not None:
                return bot_config.hardware_id

            hardware_id = generate_hardware_id()
            all_configs[login] = bot_config.model_copy(
                update={"hardware_id": hardware_id}
            )
            self._write_all_configs(all_configs)
            return hardware_id

    def remove_bot_config(self, login: str):
        with self._BOT_CONFIG_LOCK:
            all_configs = self._get_all_configs()
            all_configs.pop(login, None)
            self._write_all_configs(all_configs)
