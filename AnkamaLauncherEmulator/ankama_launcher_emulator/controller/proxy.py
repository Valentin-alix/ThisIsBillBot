from utils.local_json import read_local_model
from src.utils.runtime_support import RuntimeSetupError
from threading import RLock

from utils.singleton import Singleton

from ankama_launcher_emulator.consts import PROXIES_STORAGE_PATH
from ankama_launcher_emulator.interfaces.schedule_profile import (
    PersistedProxy,
    ProxiesFile,
    ProxyConfig,
)
from ankama_launcher_emulator.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)


class ProxyController(metaclass=Singleton):
    _LOCK = RLock()
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _load_proxies(self) -> ProxiesFile:
        if not PROXIES_STORAGE_PATH.exists():
            return ProxiesFile()
        return read_local_model(PROXIES_STORAGE_PATH, ProxiesFile)

    def _save_proxies(self, proxies_file: ProxiesFile) -> None:
        atomic_write_text(PROXIES_STORAGE_PATH, proxies_file.model_dump_json(indent=2))

    def get_proxy(self, proxy_id: str) -> PersistedProxy:
        with self._LOCK:
            proxy = self._load_proxies().proxies.get(proxy_id)
            if proxy is None:
                raise RuntimeSetupError(f"Unknown proxy: {proxy_id}. Check proxies.json.")
            return proxy

    def get_all(self) -> dict[str, PersistedProxy]:
        with self._LOCK:
            return self._load_proxies().proxies

    def save_config(self, proxy_id: str, config: ProxyConfig, *, create: bool = False) -> None:
        if not proxy_id.strip() or not config.host.strip():
            raise ValueError("Proxy identifier and host are required.")
        if not all(1 <= port <= 65535 for port in (config.http_port, config.socks_port)):
            raise ValueError("Ports must be between 1 and 65535.")
        with self._LOCK, acquire_file_lock(PROXIES_STORAGE_PATH):
            data = self._load_proxies()
            previous = data.proxies.get(proxy_id)
            if create and previous is not None:
                raise ValueError("This proxy identifier already exists.")
            if not create and previous is None:
                raise ValueError("This proxy no longer exists. Refresh the list.")
            if previous is None:
                previous = PersistedProxy(**config.model_dump())
                data.proxies[proxy_id] = previous
            previous.host = config.host
            previous.http_port = config.http_port
            previous.socks_port = config.socks_port
            previous.username = config.username
            previous.password = config.password
            self._save_proxies(data)

    def remove_config(self, proxy_id: str) -> None:
        with self._LOCK, acquire_file_lock(PROXIES_STORAGE_PATH):
            data = self._load_proxies()
            if data.proxies.pop(proxy_id, None) is not None:
                self._save_proxies(data)

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
