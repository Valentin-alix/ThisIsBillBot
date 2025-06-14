import os
import time
from dataclasses import dataclass, field

from pydantic import RootModel

from src.const import RESOURCE_FOLDER

OPERATIONS_PATH = os.path.join(RESOURCE_FOLDER, "account_operations.json")

ONE_HOUR_SEC = 3600
ONE_DAY_SEC = 86_400

MAX_OPERATIONS_PER_HOUR = 2
MAX_OPERATIONS_PER_DAY = 4


class OperationLog(RootModel[dict[str, list[float]]]):
    """Persisted form of the pool: a JSON object mapping each source IP to the
    epoch-second timestamps of operations launched on that IP."""


@dataclass
class OperationPool:
    """Per-proxy sliding-window quota tracker for account creation/authentication.

    Ankama rate-limits these operations per source network. Bot-DofusUnity uses
    SOCKS5 proxies as the only source selector, so each proxy URL carries its own
    independent budget. Each attempt consumes one token, so we record a timestamp
    the moment an operation is launched, keyed by the proxy URL.

    Timestamps are persisted to disk so the rolling windows survive restarts.
    """

    path: str = OPERATIONS_PATH
    _timestamps: dict[str, list[float]] = field(
        init=False, default_factory=dict[str, list[float]]
    )

    def __post_init__(self) -> None:
        self._timestamps = self._load()

    def _load(self) -> dict[str, list[float]]:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, encoding="utf-8") as file:
            return OperationLog.model_validate_json(file.read()).root

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(OperationLog(self._timestamps).model_dump_json())

    def _count_since(self, quota_key: str, threshold: float) -> int:
        return sum(1 for ts in self._timestamps.get(quota_key, []) if ts >= threshold)

    def has_quota(self, quota_key: str, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        within_hour = self._count_since(quota_key, now - ONE_HOUR_SEC)
        within_day = self._count_since(quota_key, now - ONE_DAY_SEC)
        return (
            within_hour < MAX_OPERATIONS_PER_HOUR
            and within_day < MAX_OPERATIONS_PER_DAY
        )

    def count_since_hour(self, quota_key: str, now: float | None = None) -> int:
        now = time.time() if now is None else now
        return self._count_since(quota_key, now - ONE_HOUR_SEC)

    def available_ip(self, ips: list[str], now: float | None = None) -> str | None:
        """Return a quota key from ``ips`` that still has quota.

        Kept for backward compatibility with older callers; Bot-DofusUnity now
        passes proxy URLs as quota keys.
        """
        now = time.time() if now is None else now
        candidates = [ip for ip in ips if self.has_quota(ip, now)]
        if not candidates:
            return None
        return min(candidates, key=lambda ip: self.count_since_hour(ip, now))

    def record(self, quota_key: str, now: float | None = None) -> None:
        now = time.time() if now is None else now
        timestamps = self._timestamps.setdefault(quota_key, [])
        timestamps.append(now)
        # Drop entries that fell out of the daily window; they can never affect
        # either quota again. Forget the IP entirely once it has none left.
        timestamps[:] = [ts for ts in timestamps if ts >= now - ONE_DAY_SEC]
        if not timestamps:
            del self._timestamps[quota_key]
        self._save()
