from enum import Enum


class TicketStatus(Enum):
    ACTIVE = "ACTIVE"
    CHECKED_IN = "CHECKED_IN"
    CANCELLED = "CANCELLED"