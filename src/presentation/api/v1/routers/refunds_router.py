from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.refund.commands.approve_refund import ApproveRefundCommand
from src.application.refund.commands.approve_refund_handler import ApproveRefundHandler
from src.application.refund.commands.mark_refund_paid_out import MarkRefundPaidOutCommand
from src.application.refund.commands.mark_refund_paid_out_handler import MarkRefundPaidOutHandler
from src.application.refund.commands.reject_refund import RejectRefundCommand
from src.application.refund.commands.reject_refund_handler import RejectRefundHandler
from src.application.refund.commands.request_refund import RequestRefundCommand
from src.application.refund.commands.request_refund_handler import RequestRefundHandler
from src.domain.shared.exceptions.domain_exception import DomainException
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.repositories.booking_repository import BookingRepository
from src.infrastructure.repositories.event_repository import EventRepository
from src.infrastructure.repositories.refund_repository import RefundRepository
from src.infrastructure.repositories.ticket_repository import TicketRepository
from src.infrastructure.services.notification.notification_service import ConsoleNotificationService
from src.infrastructure.services.refund.refund_payment_service import ConsoleRefundPaymentService

router = APIRouter(prefix="/refunds", tags=["Refunds"])


# Dependency Providers 

async def get_booking_repository(
    session: AsyncSession = Depends(get_db_session),
) -> BookingRepository:
    return BookingRepository(session)


async def get_event_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EventRepository:
    return EventRepository(session)


async def get_ticket_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TicketRepository:
    return TicketRepository(session)


async def get_refund_repository(
    session: AsyncSession = Depends(get_db_session),
) -> RefundRepository:
    return RefundRepository(session)


def get_notification_service() -> ConsoleNotificationService:
    return ConsoleNotificationService()


def get_refund_payment_service() -> ConsoleRefundPaymentService:
    return ConsoleRefundPaymentService()


# US-15 

class RequestRefundRequest(BaseModel):
    customer_id: str


@router.post("/bookings/{booking_id}/refund", status_code=201)
async def request_refund(
    booking_id: str,
    body: RequestRefundRequest,
    booking_repo: BookingRepository = Depends(get_booking_repository),
    event_repo: EventRepository = Depends(get_event_repository),
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
    refund_repo: RefundRepository = Depends(get_refund_repository),
):
    """
    US-15: Request Refund
    Customer mengajukan permintaan refund untuk booking yang sudah Paid.
    """
    handler = RequestRefundHandler(
        booking_repository=booking_repo,
        event_repository=event_repo,
        ticket_repository=ticket_repo,
        refund_repository=refund_repo,
    )
    command = RequestRefundCommand(
        booking_id=booking_id,
        customer_id=body.customer_id,
    )
    try:
        result = await handler.handle(command)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))