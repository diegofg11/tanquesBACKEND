"""
Esquemas Pydantic para la validación de datos de entrada y salida de la API.

Estos modelos garantizan que la comunicación entre el frontend (Unity/Dashboard)
y el backend sea consistente y segura.
"""
from pydantic import BaseModel

# --- Esquemas de Usuario ---

class UserCreate(BaseModel):
    """
    Datos necesarios para el registro o login de un usuario.
    """
    username: str
    password: str

class UserOut(BaseModel):
    """
    Datos públicos de un usuario que se envían al cliente.
    """
    username: str
    is_active: bool
    score: int

    class Config:
        from_attributes = True

# --- Esquemas de Puntuación ---

class ScoreSubmission(BaseModel):
    """
    Datos enviados por Unity al finalizar una partida.
    Incluye estadísticas y el token de seguridad para validar la sesión.
    """
    tiempo_segundos: int
    daño_recibido: int
    nivel_alcanzado: int  # 1, 2 o 3 (3 representa victoria)
    game_token: str | None = None  # Token JWT generado al inicio de la partida

class ScoreHistoryItem(BaseModel):
    """
    Representa una entrada individual en el historial de puntuaciones del usuario.
    """
    score: int
    nivel: int
    fecha: str  # Timestamp formateado como string para facilitar el consumo
    
class UserProfileOut(UserOut):
    """
    Esquema extendido para el perfil del usuario.
    Incluye estadísticas agregadas y el historial de partidas recientes.
    """
    total_games: int
    history: list[ScoreHistoryItem] = []
