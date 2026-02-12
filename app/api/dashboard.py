"""
Rutas de la API para el Dashboard administrativo.

Delega la lógica de agregación al `DashboardService`.
"""
from fastapi import APIRouter, Depends
from google.cloud import firestore
from app.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

def get_dashboard_service(db: firestore.Client = Depends(get_db)) -> DashboardService:
    return DashboardService(db)

@router.get("/stats")
def get_dashboard_stats(
    time_range: str = "all", 
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Recupera estadísticas globales para el dashboard.
    """
    return service.get_global_stats(time_range)

@router.get("/user/{username}")
def get_user_stats(
    username: str, 
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Busca estadísticas detalladas de un usuario específico.
    """
    return service.get_user_stats(username)
