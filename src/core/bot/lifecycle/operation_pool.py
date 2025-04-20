import logging
import os
import time
from dataclasses import dataclass, field

from pydantic import RootModel

from src.const import RESOURCE_FOLDER

logger = logging.getLogger()

OPERATIONS_PATH = os.path.join(RESOURCE_FOLDER, "account_operations.json")

ONE_HOUR_SEC = 3600
ONE_DAY_SEC = 86_400

MAX_OPERATIONS_PER_HOUR = 2
MAX_OPERATIONS_PER_DAY = 4


class OperationTimestamps(RootModel[list[float]]):
    """Persisted form of the pool: a JSON array of epoch-second timestamps."""


@dataclass
class OperationPool:
    """Sliding-window quota tracker shared by account creation and authentication.

    Ankama rate-limits these operations: at most ``MAX_OPERATIONS_PER_HOUR`` per
    rolling hour and ``MAX_OPERATIONS_PER_DAY`` per rolling day, both drawing from
    the same pool. Each *attempt* (success or failure) consumes one token, so we
    record a timestamp the moment an operation is launched.

    Timestamps are persisted to disk so the rolling window survives restarts.
    """

    path: str = OPERATIONS_PATH
    _timestamps: list[float] = field(init=False, default_factory=list[float])

    def __post_init__(self) -> None:
        self._timestamps = self._load()

    def _load(self) -> list[float]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, encoding="utf-8") as file:
            return OperationTimestamps.model_validate_json(file.read()).root

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(OperationTimestamps(self._timestamps).model_dump_json())

    def _count_since(self, threshold: float) -> int:
        return sum(1 for ts in self._timestamps if ts >= threshold)

    def has_quota(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now
        within_hour = self._count_since(now - ONE_HOUR_SEC)
        within_day = self._count_since(now - ONE_DAY_SEC)
        return (
            within_hour < MAX_OPERATIONS_PER_HOUR
            and within_day < MAX_OPERATIONS_PER_DAY
        )

    def record(self, now: float | None = None) -> None:
        now = time.time() if now is None else now
        self._timestamps.append(now)
        # Drop entries that fell out of the daily window; they can never affect
        # either quota again.
        self._timestamps = [ts for ts in self._timestamps if ts >= now - ONE_DAY_SEC]
        self._save()
