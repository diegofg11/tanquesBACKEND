from fastapi import APIRouter, Depends
from google.cloud import firestore
from app.database import get_db
from app.schemas.event import EventCreate
from app.services.event_service import EventService

router = APIRouter(
    prefix="/events",
    tags=["Eventos y Métricas"]
)

def get_event_service(db: firestore.Client = Depends(get_db)) -> EventService:
    return EventService(db)

@router.post("/")
def log_game_event(
    event: EventCreate,
    service: EventService = Depends(get_event_service)
):
    """
    Registra un evento ocurrido durante la partida.
    
    Usado para telemetría: muertes, daño, items, etc.
    """
    return service.log_event(event)

@router.get("/recent")
def get_recent_events(
    limit: int = 20,
    service: EventService = Depends(get_event_service)
):
    """
    Ver últimos eventos (para debugging o dashboard en vivo).
    """
    return service.get_recent_events(limit)
