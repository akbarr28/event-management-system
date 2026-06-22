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
    
@router.get("/{booking_id}/total-price", status_code=200)
async def get_booking_total_price(
    booking_id: str,
    booking_repo: BookingRepository = Depends(get_booking_repository),
):
    """
    US-09: Calculate Booking Total Price
    Customer melihat total harga booking sebelum bayar.
    """
    from src.domain.booking.value_objects.booking_id import BookingId
    try:
        booking = await booking_repo.find_by_id(BookingId.from_string(booking_id))
        if booking is None:
            raise HTTPException(status_code=404, detail="Booking not found.")
        total = booking.calculate_total_price()
        return {
            "booking_id": booking_id,
            "unit_price": str(booking.unit_price.amount),
            "quantity": booking.quantity,
            "total_price": str(total.amount),
            "currency": total.currency,
        }
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))