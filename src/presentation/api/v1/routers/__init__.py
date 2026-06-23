from fastapi import FastAPI
from src.presentation.api.v1.routers.events_router import router as events_router
from src.presentation.api.v1.routers.bookings_router import router as bookings_router
from src.presentation.api.v1.routers.tickets_router import router as tickets_router
from src.presentation.api.v1.routers.refunds_router import router as refunds_router

app = FastAPI()

app.include_router(events_router, prefix="/api/v1")
app.include_router(bookings_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(refunds_router, prefix="/api/v1")