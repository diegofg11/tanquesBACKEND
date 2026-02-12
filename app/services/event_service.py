from google.cloud import firestore
from fastapi import HTTPException
from datetime import datetime, timezone
import jwt
from app.schemas.event import EventCreate
from app.core.logger import get_logger

logger = get_logger("app.services.event")
SECRET_KEY = "CLAVE_SUPER_SECRETA_TANQUES_BACKEND"
ALGORITHM = "HS256"

class EventService:
    def __init__(self, db: firestore.Client):
        self.db = db
        self.events_ref = db.collection("events")

    def log_event(self, event: EventCreate):
        """
        Registra un evento del juego en Firestore vinculado a una sesión.
        """
        # 1. Validar Token (Rapido, sin DB call si es posible)
        try:
            payload = jwt.decode(event.game_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "game_session":
                raise HTTPException(status_code=403, detail="Token inválido")
            username = payload.get("sub")
        except Exception:
             raise HTTPException(status_code=403, detail="Token inválido o expirado")

        # 2. Preparar datos del evento
        event_doc = {
            "username": username,
            "type": event.event_type,
            "data": event.event_data,
            "timestamp": datetime.now(timezone.utc)
        }

        # 3. Guardar (Fire & Forget idealmente, pero aquí esperamos por seguridad)
        # Guardamos en una colección root 'events' para métricas globales fáciles
        self.events_ref.add(event_doc)
        logger.info(f"Evento registrado [{username}]: {event.event_type}")

        return {"status": "ok", "event_id": "logged"}

    def get_recent_events(self, limit: int = 50):
        """
        Para debug o dashboard en tiempo real.
        """
        query = self.events_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [d.to_dict() for d in query]
