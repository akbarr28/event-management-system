from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.booking.commands.create_booking import CreateBookingCommand
from src.application.booking.commands.create_booking_handler import CreateBookingHandler
from src.domain.shared.exceptions.domain_exception import DomainException
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.repositories.booking_repository import BookingRepository
from src.infrastructure.repositories.event_repository import EventRepository

router = APIRouter(prefix="/bookings", tags=["Bookings"])


async def get_event_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EventRepository:
    return EventRepository(session)


async def get_booking_repository(
    session: AsyncSession = Depends(get_db_session),
) -> BookingRepository:
    return BookingRepository(session)


class CreateBookingRequest(BaseModel):
    customer_id: str
    event_id: str
    ticket_category_id: str
    quantity: int


@router.post("/", status_code=201)
async def create_booking(
    body: CreateBookingRequest,
    event_repo: EventRepository = Depends(get_event_repository),
    booking_repo: BookingRepository = Depends(get_booking_repository),
):
    """
    US-08: Create Ticket Booking
    Customer memesan tiket untuk event Published.
    """
    handler = CreateBookingHandler(
        event_repository=event_repo,
        booking_repository=booking_repo,
    )
    command = CreateBookingCommand(
        customer_id=body.customer_id,
        event_id=body.event_id,
        ticket_category_id=body.ticket_category_id,
        quantity=body.quantity,
    )
    try:
        result = await handler.handle(command)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))