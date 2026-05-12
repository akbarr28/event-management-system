from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TicketCategoryId:
    value: UUID

    @staticmethod
    def generate() -> "TicketCategoryId":
        return TicketCategoryId(value=uuid4())

    @staticmethod
    def from_string(value: str) -> "TicketCategoryId":
        return TicketCategoryId(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)