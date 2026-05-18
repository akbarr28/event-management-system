from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TicketId:
    value: UUID

    @staticmethod
    def generate() -> "TicketId":
        return TicketId(value=uuid4())

    @staticmethod
    def from_string(value: str) -> "TicketId":
        return TicketId(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)