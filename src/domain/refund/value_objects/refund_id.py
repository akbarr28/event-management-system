from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class RefundId:
    value: UUID

    @staticmethod
    def generate() -> "RefundId":
        return RefundId(value=uuid4())

    @staticmethod
    def from_string(value: str) -> "RefundId":
        return RefundId(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)