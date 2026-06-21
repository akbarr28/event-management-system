from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.event.commands.create_event import CreateEventCommand
from src.application.event.commands.create_event_handler import CreateEventHandler
from src.domain.shared.exceptions.domain_exception import DomainException
from src.infrastructure.database.connection import get_db_session
from src.infrastructure.repositories.event_repository import EventRepository
from src.application.event.commands.publish_event import PublishEventCommand
from src.application.event.commands.publish_event_handler import PublishEventHandler
from src.application.event.commands.cancel_event import CancelEventCommand
from src.application.event.commands.cancel_event_handler import CancelEventHandler


router = APIRouter(prefix="/events", tags=["Events"])


async def get_event_repository(
    session: AsyncSession = Depends(get_db_session),
) -> EventRepository:
    return EventRepository(session)


class CreateEventRequest(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    location: str
    maximum_capacity: int
    organizer_id: str

class PublishEventRequest(BaseModel):
    organizer_id: str

class CancelEventRequest(BaseModel):
    organizer_id: str

@router.post("/", status_code=201)
async def create_event(
    body: CreateEventRequest,
    event_repo: EventRepository = Depends(get_event_repository),
):
    """
    US-01: Create Event
    Event Organizer membuat event baru dengan status Draft.
    """
    handler = CreateEventHandler(event_repository=event_repo)
    command = CreateEventCommand(
        name=body.name,
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date,
        location=body.location,
        maximum_capacity=body.maximum_capacity,
        organizer_id=body.organizer_id,
    )
    try:
        result = await handler.handle(command)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))
    

@router.post("/{event_id}/publish", status_code=200)
async def publish_event(
    event_id: str,
    body: PublishEventRequest,
    event_repo: EventRepository = Depends(get_event_repository),
):
    """
    US-02: Publish Event
    Event Organizer mempublish event Draft agar bisa dilihat customer.
    """
    handler = PublishEventHandler(event_repository=event_repo)
    command = PublishEventCommand(
        event_id=event_id,
        organizer_id=body.organizer_id,
    )
    try:
        result = await handler.handle(command)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))
    
@router.post("/{event_id}/cancel", status_code=200)
async def cancel_event(
    event_id: str,
    body: CancelEventRequest,
    event_repo: EventRepository = Depends(get_event_repository),
):
    """
    US-03: Cancel Event
    Event Organizer membatalkan event Published.
    """
    handler = CancelEventHandler(event_repository=event_repo)
    command = CancelEventCommand(
        event_id=event_id,
        organizer_id=body.organizer_id,
    )
    try:
        result = await handler.handle(command)
        return result
    except DomainException as e:
        raise HTTPException(status_code=422, detail=str(e))