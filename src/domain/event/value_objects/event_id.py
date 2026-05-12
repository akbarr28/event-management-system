from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EventId:
    value: UUID

    @staticmethod
    def generate() -> "EventId":
        return EventId(value=uuid4())

    @staticmethod
    def from_string(value: str) -> "EventId":
        return EventId(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)