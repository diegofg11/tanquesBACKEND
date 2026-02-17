"""
Rutas de la API para la gestión de usuarios y puntuaciones.

Delegan la lógica de negocio a los servicios `UserService` y `ScoreService`.
"""
from fastapi import APIRouter, Depends
from google.cloud import firestore
from app.database import get_db
from app.database import get_db
from app.schemas.user import UserCreate, UserOut, ScoreSubmission, UserProfileOut
from app.services.user_service import UserService

from app.services.score_service import ScoreService
from app.db_sql import get_db_sql
from app.services import audit_service
from sqlalchemy.orm import Session


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
    service: UserService = Depends(get_user_service),
    db_audit: Session = Depends(get_db_sql)
):
    """
    Registra un nuevo usuario en el sistema.
    """
    user = service.register_user(user_data)
    # Auditoría con SQLAlchemy
    audit_service.log_audit(db_audit, user_id=user.uid, action="User Registered", username=user.username)
    return user


@router.post("/login")
def login(
    user_data: UserCreate, 
    service: UserService = Depends(get_user_service),
    db_audit: Session = Depends(get_db_sql)
):
    """
    Autentica a un usuario y retorna mensaje de éxito.
    """
    service.authenticate_user(user_data)
    # Como authenticate no devuelve el UID, usamos el username como referencia o deberíamos buscar el usuario.
    # Para simplificar y no hacer una doble query a Firebase, logueamos el intento exitoso con el username.
    audit_service.log_audit(db_audit, user_id=user_data.username, action="User Login", username=user_data.username)
    return {"mensaje": "Autenticación exitosa", "username": user_data.username}

@router.post("/{username}/start-game")
def start_game(
    username: str, 
    service: ScoreService = Depends(get_score_service),
    db_audit: Session = Depends(get_db_sql)
):

    """
    Inicia una sesión y devuelve un token de juego.
    """
    token = service.create_game_token(username)
    audit_service.log_audit(db_audit, user_id=username, action="Game Started", username=username)
    return {"game_token": token}

@router.post("/{username}/submit-score")
def submit_score(
    username: str, 
    stats: ScoreSubmission, 
    service: ScoreService = Depends(get_score_service),
    db_audit: Session = Depends(get_db_sql)
):
    """
    Recibe y procesa la puntuación final de una partida.
    """
    result = service.submit_score(username, stats)
    audit_service.log_audit(db_audit, user_id=username, action=f"Score Submitted: {stats.score}", username=username)
    return result

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
