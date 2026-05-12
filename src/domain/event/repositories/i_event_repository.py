from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.event.aggregates.event import Event
from src.domain.event.value_objects.event_id import EventId


class IEventRepository(ABC):

    @abstractmethod
    async def save(self, event: Event) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, event_id: EventId) -> Optional[Event]:
        raise NotImplementedError

    @abstractmethod
    async def find_published(self) -> List[Event]:
        raise NotImplementedError