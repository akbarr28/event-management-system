from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class BookingId:
    value: UUID

    @staticmethod
    def generate() -> "BookingId":
        return BookingId(value=uuid4())

    @staticmethod
    def from_string(value: str) -> "BookingId":
        return BookingId(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)