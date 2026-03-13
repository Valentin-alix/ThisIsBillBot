import time
from dataclasses import dataclass, field

from ankama_launcher_emulator.controller.proxy import ProxyController

ONE_HOUR_SEC = 3600
ONE_DAY_SEC = 86_400
REGISTER_PROXY_COOLDOWN_SEC = 6 * ONE_HOUR_SEC

MAX_OPERATIONS_PER_HOUR = 2
MAX_OPERATIONS_PER_DAY = 4


@dataclass
class OperationPool:
    """Creation and authentication share a persisted per-proxy quota, consumed when each attempt starts."""

    proxy_controller: ProxyController = field(default_factory=ProxyController)
    _timestamps: dict[str, list[float]] = field(init=False, default_factory=dict[str, list[float]])
    _register_cooldowns: dict[str, float] = field(init=False, default_factory=dict[str, float])

    def __post_init__(self) -> None:
        self._timestamps = self.proxy_controller.get_operation_timestamps()
        self._register_cooldowns = self.proxy_controller.get_register_cooldowns()

    def _save_proxy(self, proxy_id: str) -> None:
        self.proxy_controller.update_proxy_runtime(
            proxy_id,
            self._timestamps.get(proxy_id, []),
            self._register_cooldowns.get(proxy_id),
        )

    def _count_since(self, proxy_id: str, threshold: float) -> int:
        return sum(1 for timestamp in self._timestamps.get(proxy_id, []) if timestamp >= threshold)

    def has_quota(self, proxy_id: str, now: float | None = None) -> bool:
        return self.has_quota_for(proxy_id, 1, now)

    def has_quota_for(self, proxy_id: str, count: int, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        within_hour = self._count_since(proxy_id, now - ONE_HOUR_SEC)
        within_day = self._count_since(proxy_id, now - ONE_DAY_SEC)
        return within_hour + count <= MAX_OPERATIONS_PER_HOUR and within_day + count <= MAX_OPERATIONS_PER_DAY

    def count_since_hour(self, proxy_id: str, now: float | None = None) -> int:
        now = time.time() if now is None else now
        return self._count_since(proxy_id, now - ONE_HOUR_SEC)

    def is_register_cooled_down(self, proxy_id: str, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        expires_at = self._register_cooldowns.get(proxy_id)
        if expires_at is None:
            return False
        if expires_at > now:
            return True
        del self._register_cooldowns[proxy_id]
        self._save_proxy(proxy_id)
        return False

    def record_register_cooldown(self, proxy_id: str, now: float | None = None) -> None:
        now = time.time() if now is None else now
        self._register_cooldowns[proxy_id] = now + REGISTER_PROXY_COOLDOWN_SEC
        self._save_proxy(proxy_id)

    def record(self, proxy_id: str, now: float) -> None:
        timestamps = self._timestamps.setdefault(proxy_id, [])
        timestamps.append(now)

        timestamps[:] = [ts for ts in timestamps if ts >= now - ONE_DAY_SEC]
        if not timestamps:
            del self._timestamps[proxy_id]
        self._save_proxy(proxy_id)
