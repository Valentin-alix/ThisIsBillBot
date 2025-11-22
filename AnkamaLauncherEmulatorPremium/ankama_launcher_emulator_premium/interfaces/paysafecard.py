from datetime import datetime
from enum import StrEnum

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
    updated_at: datetime
