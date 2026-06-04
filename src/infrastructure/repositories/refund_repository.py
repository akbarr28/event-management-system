from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.booking.value_objects.booking_id import BookingId
from src.domain.booking.value_objects.customer_id import CustomerId
from src.domain.refund.aggregates.refund import Refund
from src.domain.refund.repositories.i_refund_repository import IRefundRepository
from src.domain.refund.value_objects.refund_id import RefundId
from src.domain.refund.value_objects.refund_status import RefundStatus
from src.domain.shared.value_objects.money import Money
from src.infrastructure.database.models.refund_model import RefundModel


class RefundRepository(IRefundRepository):

    def __init__(self, session: AsyncSession):
        self._session = session

    # ---------- save ----------

    async def save(self, refund: Refund) -> None:
        existing = await self._session.get(RefundModel, refund.id.value)
        if existing is None:
            self._session.add(self._to_model(refund))
        else:
            self._update_model(existing, refund)
        await self._session.flush()

    # ---------- find_by_id ----------

    async def find_by_id(self, refund_id: RefundId) -> Optional[Refund]:
        result = await self._session.get(RefundModel, refund_id.value)
        if result is None:
            return None
        return self._to_domain(result)

    # ---------- find_by_booking_id ----------

    async def find_by_booking_id(self, booking_id: BookingId) -> Optional[Refund]:
        stmt = select(RefundModel).where(
            RefundModel.booking_id == booking_id.value
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    # ---------- mapping helpers ----------

    def _to_model(self, refund: Refund) -> RefundModel:
        return RefundModel(
            id=refund.id.value,
            booking_id=refund.booking_id.value,
            customer_id=refund.customer_id.value,
            amount=refund.amount.amount,
            currency=refund.amount.currency,
            status=refund.status.value,
            rejection_reason=refund.rejection_reason,
            payment_reference=refund.payment_reference,
        )

    def _update_model(self, model: RefundModel, refund: Refund) -> None:
        model.status = refund.status.value
        model.rejection_reason = refund.rejection_reason
        model.payment_reference = refund.payment_reference

    def _to_domain(self, model: RefundModel) -> Refund:
        return Refund(
            id=RefundId(value=model.id),
            booking_id=BookingId(value=model.booking_id),
            customer_id=CustomerId(value=model.customer_id),
            amount=Money(
                amount=Decimal(str(model.amount)),
                currency=model.currency,
            ),
            status=RefundStatus(model.status),
            rejection_reason=model.rejection_reason,
            payment_reference=model.payment_reference,
        )