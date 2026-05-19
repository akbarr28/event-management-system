from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class RefundDTO:
    """DTO untuk detail refund — US-15 s/d US-18."""
    id: str
    booking_id: str
    customer_id: str
    amount: Decimal
    currency: str
    status: str
    rejection_reason: Optional[str]
    payment_reference: Optional[str]
    occurred_at: datetime