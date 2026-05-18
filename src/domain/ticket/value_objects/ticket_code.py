from dataclasses import dataclass
from uuid import uuid4

from src.domain.shared.exceptions.domain_exception import DomainException


@dataclass(frozen=True)
class TicketCode:
    value: str

    @staticmethod
    def generate() -> "TicketCode":
        return TicketCode(value=str(uuid4()).replace("-", "").upper()[:12])

    def __str__(self) -> str:
        return self.value