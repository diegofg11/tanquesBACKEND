"""
Esquemas Pydantic para la gestión de Eventos del juego.
"""
from pydantic import BaseModel
from typing import Dict, Any, Optional

class EventCreate(BaseModel):
    """
    Representa un evento enviado desde el cliente (Unity).

    Attributes:
        game_token (str): Token de sesión para validar la partida.
        event_type (str): Tipo de evento (ej: "ENEMY_KILLED", "LEVEL_START").
        event_data (dict): Metadatos adicionales del evento (ej: daño, tipo de enemigo).
    """
    game_token: str
    event_type: str 
    event_data: Optional[Dict[str, Any]] = {} 
