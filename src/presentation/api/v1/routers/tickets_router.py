from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ticket.queries.get_purchased_tickets import GetPurchasedTicketsQuery
from src.application.ticket.queries.get_purchased_tickets_handler import GetPurchasedTicketsHandler
from src.domain.shared.exceptions.domain_exception import DomainException
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.repositories.booking_repository import BookingRepository
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