from threading import RLock
from typing import Literal

from base_python.singleton import Singleton
from pydantic import BaseModel, Field

from ankama_launcher_emulator_premium.consts import (
    PROXIES_STORAGE_PATH,
    SCHEDULE_PROFILES_PATH,
)
from ankama_launcher_emulator_premium.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)
from ankama_launcher_emulator_premium.utils.proxy import ProxyConfig


class TimeSlot(BaseModel):
    start: str
    end: str


class ScheduleProfile(BaseModel):
    name_fr: str
    proxy_id: str
    slots_by_day: dict[str, list[TimeSlot]]
    mule_give_slot: TimeSlot | None = None
    kind: Literal["bot", "kamas_mule"] = "bot"


class ScheduleProfiles(BaseModel):
    profiles: dict[str, ScheduleProfile]


class PersistedProxy(ProxyConfig):
    operation_timestamps: list[float] = Field(default_factory=list[float])
    register_cooldown_until: float | None = None


class ProxiesFile(BaseModel):
    proxies: dict[str, PersistedProxy] = Field(default_factory=dict[str, PersistedProxy])


class ScheduleProfileController(metaclass=Singleton):
    _LOCK = RLock()

    def get_all_profiles(self) -> dict[str, ScheduleProfile]:
        with self._LOCK:
            return ScheduleProfiles.model_validate_json(
                SCHEDULE_PROFILES_PATH.read_text(encoding="utf-8")
            ).profiles

    def get_profile(self, profile_id: str) -> ScheduleProfile | None:
        return self.get_all_profiles().get(profile_id)

    def get_profile_display_names(self) -> dict[str, str]:
        return {
            profile_id: f"{profile_id} - {profile.name_fr}"
            for profile_id, profile in self.get_all_profiles().items()
        }


class ProxyController(metaclass=Singleton):
    _LOCK = RLock()
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _load_proxies(self) -> ProxiesFile:
        if not PROXIES_STORAGE_PATH.exists():
            return ProxiesFile()
        return ProxiesFile.model_validate_json(PROXIES_STORAGE_PATH.read_text(encoding="utf-8"))

    def _save_proxies(self, proxies_file: ProxiesFile) -> None:
        atomic_write_text(PROXIES_STORAGE_PATH, proxies_file.model_dump_json(indent=2))

    def get_proxy(self, proxy_id: str) -> PersistedProxy:
        with self._LOCK:
            proxy = self._load_proxies().proxies.get(proxy_id)
            if proxy is None:
                raise ValueError(f"Unknown proxy {proxy_id}")
            return proxy

    def record_rejection(self, proxy_id: str) -> None:
        with (
            self._LOCK,
            acquire_file_lock(PROXIES_STORAGE_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS),
        ):
            proxies_file = self._load_proxies()
            proxy = proxies_file.proxies.get(proxy_id)
            if proxy is None:
                raise ValueError(f"Unknown proxy {proxy_id}")
            proxy.rejected = True
            self._save_proxies(proxies_file)

    def get_operation_timestamps(self) -> dict[str, list[float]]:
        with self._LOCK:
            return {
                proxy_id: list(proxy.operation_timestamps)
                for proxy_id, proxy in self._load_proxies().proxies.items()
            }

    def get_register_cooldowns(self) -> dict[str, float]:
        with self._LOCK:
            return {
                proxy_id: proxy.register_cooldown_until
                for proxy_id, proxy in self._load_proxies().proxies.items()
                if proxy.register_cooldown_until is not None
            }

    def update_proxy_runtime(
        self,
        proxy_id: str,
        operation_timestamps: list[float],
        register_cooldown_until: float | None,
    ) -> None:
        with (
            self._LOCK,
            acquire_file_lock(PROXIES_STORAGE_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS),
        ):
            proxies_file = self._load_proxies()
            proxy = proxies_file.proxies.get(proxy_id)
            if proxy is None:
                raise ValueError(f"Unknown proxy {proxy_id}")
            proxy.operation_timestamps = operation_timestamps
            proxy.register_cooldown_until = register_cooldown_until
            self._save_proxies(proxies_file)
