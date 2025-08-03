from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from threading import Lock

from pydantic import BaseModel, ConfigDict


class PaysafecardPurchaseStatus(StrEnum):
    RESERVED = "reserved"
    AWAITING_CONFIRMATION = "awaiting_confirmation"


class PaysafecardPurchase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    login: str
    pin: str
    status: PaysafecardPurchaseStatus
    order_id: str | None = None
    xsolla_token: str | None = None
    updated_at: datetime


class PaysafecardPurchaseStorage:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = Lock()

    def load_purchase(self) -> PaysafecardPurchase | None:
        with self._lock:
            if not self._path.exists():
                return None
            return PaysafecardPurchase.model_validate_json(self._path.read_text(encoding="utf-8"))

    def record_purchase(self, purchase: PaysafecardPurchase) -> None:
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                purchase.model_dump_json(indent=2),
                encoding="utf-8",
            )

    def reserve_purchase(self, login: str, pin: str) -> PaysafecardPurchase:
        purchase = PaysafecardPurchase(
            login=login,
            pin=pin,
            status=PaysafecardPurchaseStatus.RESERVED,
            updated_at=datetime.now(UTC),
        )
        self.record_purchase(purchase)
        return purchase

    def record_awaiting_confirmation(
        self,
        purchase: PaysafecardPurchase,
        *,
        order_id: str,
        xsolla_token: str,
    ) -> PaysafecardPurchase:
        updated_purchase = purchase.model_copy(
            update={
                "status": PaysafecardPurchaseStatus.AWAITING_CONFIRMATION,
                "order_id": order_id,
                "xsolla_token": xsolla_token,
                "updated_at": datetime.now(UTC),
            }
        )
        self.record_purchase(updated_purchase)
        return updated_purchase

    def clear_purchase(self) -> None:
        with self._lock:
            self._path.unlink(missing_ok=True)
