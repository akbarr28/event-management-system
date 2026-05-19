from dataclasses import dataclass


@dataclass(frozen=True)
class ParticipantDTO:
    customer_name: str
    ticket_category_name: str
    ticket_code: str
    is_checked_in: bool