import json
import os
from threading import RLock
from typing import Literal

from ankama_launcher_emulator_premium.decrypter.hardware_identity import (
    generate_hardware_id,
)
from consts import PC_ID
from pydantic import BaseModel, RootModel
from python_utils.singleton import Singleton

from src.const import RESOURCE_FOLDER
from src.controller.schedule_profile_controller import ScheduleProfileController


class BotConfig(BaseModel):
    network_interface: str | None = None
    pc_id: int = PC_ID
    schedule_profile: str | None = None
    connection_mode: Literal["mitm", "socket"] = "mitm"
    hardware_id: str | None = None
    auto_subscribe: bool = True
    subscribe_server_name: str | None = None


class BotConfigs(RootModel):
    root: dict[str, BotConfig]


class BotConfigController(metaclass=Singleton):
    _BOT_CONFIG_LOCK = RLock()
    _BOT_CONFIG_PATH = os.path.join(RESOURCE_FOLDER, "bot_configs.json")

    def _get_all_configs(self) -> dict[str, BotConfig]:
        with open(self._BOT_CONFIG_PATH, "r") as file:
            return BotConfigs.model_validate(json.load(file)).root

    def _write_all_configs(self, bot_configs: dict[str, BotConfig]) -> None:
        with open(self._BOT_CONFIG_PATH, "w") as file:
            json.dump(BotConfigs(root=bot_configs).model_dump(), file, indent=2)

    def get_bot_config_by_login(self) -> dict[str, BotConfig]:
        with self._BOT_CONFIG_LOCK:
            return {
                key: value
                for key, value in self._get_all_configs().items()
                if value.pc_id == PC_ID
            }

    def update_bot_config_by_login(self, bot_config: BotConfig, login: str):
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

    def assign_least_used_network_interface(
        self, login: str, available_interfaces: list[str]
    ) -> str | None:
        """Assign the least represented network interface to ``login`` and persist it.

        Balances accounts across available interfaces. Returns the chosen IP, or
        None when no interfaces are available.
        """
        if not available_interfaces:
            return None
        with self._BOT_CONFIG_LOCK:
            all_configs = self._get_all_configs()
            counts = {ip: 0 for ip in available_interfaces}
            for config in all_configs.values():
                if config.pc_id == PC_ID and config.network_interface in counts:
                    counts[config.network_interface] += 1
            chosen = min(sorted(counts), key=lambda ip: counts[ip])
            existing = all_configs.get(login, BotConfig())
            all_configs[login] = existing.model_copy(
                update={"network_interface": chosen}
            )
            self._write_all_configs(all_configs)
        return chosen

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
