from datetime import UTC, datetime

from utils.singleton import Singleton
from filelock import FileLock

from ankama_launcher_emulator.consts import PAYSAFECARD_PURCHASE_PATH
from ankama_launcher_emulator.interfaces.paysafecard import (
    PaysafecardPurchase,
    PaysafecardPurchaseStatus,
)
from ankama_launcher_emulator.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)


class PaysafecardPurchaseController(metaclass=Singleton):
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _acquire_file_lock(self) -> FileLock:
        return acquire_file_lock(PAYSAFECARD_PURCHASE_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS)

    def load_purchase(self) -> PaysafecardPurchase | None:
        with self._acquire_file_lock():
            if not PAYSAFECARD_PURCHASE_PATH.exists():
                return None
            return PaysafecardPurchase.model_validate_json(
                PAYSAFECARD_PURCHASE_PATH.read_text(encoding="utf-8")
            )

    def record_purchase(self, purchase: PaysafecardPurchase) -> None:
        with self._acquire_file_lock():
            atomic_write_text(PAYSAFECARD_PURCHASE_PATH, purchase.model_dump_json(indent=2))

    def reserve_purchase(self, login: str, pin: str) -> PaysafecardPurchase | None:
        with self._acquire_file_lock():
            if PAYSAFECARD_PURCHASE_PATH.exists():
                return None
            purchase = PaysafecardPurchase(
                login=login,
                pin=pin,
                status=PaysafecardPurchaseStatus.RESERVED,
                updated_at=datetime.now(UTC),
            )
            atomic_write_text(PAYSAFECARD_PURCHASE_PATH, purchase.model_dump_json(indent=2))
            return purchase

    def record_awaiting_confirmation(
        self,
        purchase: PaysafecardPurchase,
        *,
        order_id: str,
    ) -> PaysafecardPurchase:
        updated_purchase = purchase.model_copy(
            update={
                "status": PaysafecardPurchaseStatus.AWAITING_CONFIRMATION,
                "order_id": order_id,
                "updated_at": datetime.now(UTC),
            }
        )
        self.record_purchase(updated_purchase)
        return updated_purchase

    def clear_purchase(self) -> None:
        with self._acquire_file_lock():
            PAYSAFECARD_PURCHASE_PATH.unlink(missing_ok=True)
