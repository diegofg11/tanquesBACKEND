"""
Rutas de la API para la gestión de usuarios y puntuaciones.

Delegan la lógica de negocio a los servicios `UserService` y `ScoreService`.
"""
from fastapi import APIRouter, Depends
from google.cloud import firestore
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, ScoreSubmission, UserProfileOut
from app.services.user_service import UserService
from app.services.score_service import ScoreService

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

# --- DEPENDENCIAS DE SERVICIOS ---
def get_user_service(db: firestore.Client = Depends(get_db)) -> UserService:
    return UserService(db)

def get_score_service(db: firestore.Client = Depends(get_db)) -> ScoreService:
    return ScoreService(db)

# --- RUTAS ---

@router.post("/register", response_model=UserOut)
def register_user(
    user_data: UserCreate, 
    service: UserService = Depends(get_user_service)
):
    """
    Registra un nuevo usuario en el sistema.
    """
    return service.register_user(user_data)

@router.post("/login")
def login(
    user_data: UserCreate, 
    service: UserService = Depends(get_user_service)
):
    """
    Autentica a un usuario y retorna mensaje de éxito.
    """
    service.authenticate_user(user_data)
    return {"mensaje": "Autenticación exitosa", "username": user_data.username}

@router.post("/{username}/start-game")
def start_game(
    username: str, 
    service: ScoreService = Depends(get_score_service)
):
    """
    Inicia una sesión y devuelve un token de juego.
    """
    token = service.create_game_token(username)
    return {"game_token": token}

@router.post("/{username}/submit-score")
def submit_score(
    username: str, 
    stats: ScoreSubmission, 
    service: ScoreService = Depends(get_score_service)
):
    """
    Recibe y procesa la puntuación final de una partida.
    """
    return service.submit_score(username, stats)

@router.get("/ranking/top")
def get_top_scores(
    service: ScoreService = Depends(get_score_service)
):
    """
    Devuelve el Top 10 global.
    """
    return service.get_top_ranking(10)

@router.get("/{username}", response_model=UserProfileOut)
def get_user_profile(
    username: str, 
    service: UserService = Depends(get_user_service)
):
    """
    Devuelve el perfil completo del usuario con historial.
    """
    return service.get_user_profile(username)
