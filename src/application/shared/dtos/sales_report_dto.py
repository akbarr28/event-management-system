from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class TicketCategorySalesDTO:
    category_name: str
    tickets_sold: int


@dataclass(frozen=True)
class SalesReportDTO:
    event_id: str
    event_name: str
    tickets_sold_per_category: List[TicketCategorySalesDTO]
    total_pending_payment: int
    total_paid: int
    total_expired: int
    total_refunded: int
    total_revenue_amount: Decimal
    total_revenue_currency: str