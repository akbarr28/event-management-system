from enum import Enum


class TicketCategoryDisplayStatus(Enum):
    AVAILABLE = "AVAILABLE"
    COMING_SOON = "COMING_SOON"
    SALES_CLOSED = "SALES_CLOSED"
    SOLD_OUT = "SOLD_OUT"