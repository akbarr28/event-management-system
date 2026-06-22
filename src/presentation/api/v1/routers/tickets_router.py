from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ticket.commands.check_in_ticket import CheckInTicketCommand
from src.application.ticket.commands.check_in_ticket_handler import CheckInTicketHandler
from src.application.ticket.queries.get_purchased_tickets import GetPurchasedTicketsQuery
from src.application.ticket.queries.get_purchased_tickets_handler import GetPurchasedTicketsHandler
from src.domain.shared.exceptions.domain_exception import DomainException
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.repositories.booking_repository import BookingRepository
from src.infrastructure.repositories.event_repository import EventRepository
from src.infrastructure.repositories.ticket_repository import TicketRepository

router = APIRouter(prefix="/tickets", tags=["Tickets"])


async def get_booking_repository(
    session: AsyncSession = Depends(get_db_session),
) -> BookingRepository:
    return BookingRepository(session)


async def get_ticket_repository(
    session: AsyncSession = Depends(get_db_session),
) -> TicketRepository:
    return TicketRepository(session)


async def get_event_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EventRepository:
    return EventRepository(session)


# US-12 

@router.get("/my-tickets", status_code=200)
async def get_purchased_tickets(
    customer_id: str,
    booking_repo: BookingRepository = Depends(get_booking_repository),
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
):
    """
    US-12: View Purchased Tickets
    Customer melihat semua tiket dari booking yang sudah Paid.
    """
    handler = GetPurchasedTicketsHandler(
        booking_repository=booking_repo,
        ticket_repository=ticket_repo,
    )
    query = GetPurchasedTicketsQuery(customer_id=customer_id)
    try:
        result = await handler.handle(query)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))


# US-13 dan US-14 

class CheckInTicketRequest(BaseModel):
    ticket_code: str
    event_id: str


@router.post("/check-in", status_code=200)
async def check_in_ticket(
    body: CheckInTicketRequest,
    ticket_repo: TicketRepository = Depends(get_ticket_repository),
    event_repo: EventRepository = Depends(get_event_repository),
):
    """
    US-13 & US-14: Check In Ticket / Reject Invalid Check-in
    Gate Officer memvalidasi tiket saat peserta masuk venue.
    Menangani semua skenario rejection secara otomatis.
    """
    handler = CheckInTicketHandler(
        ticket_repository=ticket_repo,
        event_repository=event_repo,
    )
    command = CheckInTicketCommand(
        ticket_code=body.ticket_code,
        event_id=body.event_id,
    )
    try:
        await handler.handle(command)
        return {"message": "Ticket checked in successfully."}
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))