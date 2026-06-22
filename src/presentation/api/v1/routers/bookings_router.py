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
from src.application.booking.commands.pay_booking import PayBookingCommand
from src.application.booking.commands.pay_booking_handler import PayBookingHandler
from src.infrastructure.repositories.ticket_repository import TicketRepository
from src.application.booking.commands.expire_booking import ExpireBookingCommand
from src.application.booking.commands.expire_booking_handler import ExpireBookingHandler

router = APIRouter(prefix="/bookings", tags=["Bookings"])


async def get_event_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EventRepository:
    return EventRepository(session)


async def get_booking_repository(
    session: AsyncSession = Depends(get_db_session),
) -> BookingRepository:
    return BookingRepository(session)

async def get_ticket_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TicketRepository:
    return TicketRepository(session)


class PayBookingRequest(BaseModel):
    customer_id: str
    payment_amount: Decimal
    currency: str = "IDR"


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
    
@router.post("/{booking_id}/pay", status_code=200)
async def pay_booking(
    booking_id: str,
    body: PayBookingRequest,
    booking_repo: BookingRepository = Depends(get_booking_repository),
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
):
    """
    US-10: Pay Booking
    Customer membayar booking dengan jumlah yang sesuai total price.
    Setelah berhasil, ticket diterbitkan otomatis.
    """
    handler = PayBookingHandler(
        booking_repository=booking_repo,
        ticket_repository=ticket_repo,
    )
    command = PayBookingCommand(
        booking_id=booking_id,
        customer_id=body.customer_id,
        payment_amount=body.payment_amount,
        currency=body.currency,
    )
    try:
        result = await handler.handle(command)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))
    
@router.post("/{booking_id}/expire", status_code=200)
async def expire_booking(
    booking_id: str,
    booking_repo: BookingRepository = Depends(get_booking_repository),
    event_repo: EventRepository = Depends(get_event_repository),
):
    """
    US-11: Expire Booking
    System menandai booking PendingPayment sebagai Expired setelah deadline lewat.
    Quota yang direservasi dilepas kembali.
    """
    handler = ExpireBookingHandler(
        booking_repository=booking_repo,
        event_repository=event_repo,
    )
    command = ExpireBookingCommand(booking_id=booking_id)
    try:
        result = await handler.handle(command)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))