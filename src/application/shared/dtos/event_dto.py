from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class TicketCategoryDTO:
    """DTO untuk ticket category dalam event detail."""
    id: str
    name: str
    price: Decimal
    currency: str
    quota: int
    remaining_quota: int
    sales_start_date: datetime
    sales_end_date: datetime
    status: str
    display_status: str


@dataclass(frozen=True)
class EventSummaryDTO:
    """DTO untuk list event — US-06 View Available Events."""
    id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    organizer_id: str
    status: str
    lowest_price: Optional[Decimal]
    lowest_price_currency: str


@dataclass(frozen=True)
class EventDetailDTO:
    """DTO untuk detail event — US-07 View Event Details."""
    id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    organizer_id: str
    status: str
    maximum_capacity: int
    ticket_categories: List[TicketCategoryDTO]