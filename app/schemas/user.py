"""
Esquemas Pydantic para validación de datos de entrada/salida de la API.
"""
from pydantic import BaseModel

# --- Esquemas de Usuario ---

class UserCreate(BaseModel):
    """Esquema para el registro de usuarios."""
    username: str
    password: str

class UserOut(BaseModel):
    """Esquema para mostrar datos públicos del usuario."""
    username: str
    is_active: bool
    score: int

    class Config:
        from_attributes = True

# --- Esquemas de Puntuación ---

class ScoreSubmission(BaseModel):
    """
    Esquema para recibir estadísticas de final de partida.
    """
    tiempo_segundos: int
    daño_recibido: int
    nivel_alcanzado: int # 1, 2 o 3 (3 es victoria)
    game_token: str | None = None # Token de seguridad (JWT)

class ScoreHistoryItem(BaseModel):
    """Esquema para mostrar una partida en el historial."""
    score: int
    nivel: int
    fecha: str # Timestamp formateado
    
class UserProfileOut(UserOut):
    """Esquema perfil completo con historial."""
    total_games: int
    history: list[ScoreHistoryItem] = []
