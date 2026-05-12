from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "IDR"

    def __post_init__(self):
        if self.amount < Decimal("0"):
            raise ValueError("Money amount cannot be negative.")
        if not self.currency:
            raise ValueError("Currency cannot be empty.")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add Money with different currencies.")
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def multiply(self, factor: int) -> "Money":
        if factor < 0:
            raise ValueError("Multiplication factor cannot be negative.")
        return Money(amount=self.amount * Decimal(factor), currency=self.currency)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency={self.currency})"