from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class CustomerId:
    value: UUID

    @staticmethod
    def generate() -> "CustomerId":
        return CustomerId(value=uuid4())

    @staticmethod
    def from_string(value: str) -> "CustomerId":
        return CustomerId(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)