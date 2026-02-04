from fastapi import APIRouter, Depends
from google.cloud import firestore
from app.database import get_db
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def get_dashboard_stats(db: firestore.Client = Depends(get_db)):
    """
    Recupera estadísticas agregadas para el Dashboard.
    """
    # 1. Total Usuarios
    users_ref = db.collection("users")
    total_users = len(list(users_ref.list_documents()))

    # 2. Total Partidas y Distribución por Nivel
    scores_ref = db.collection("scores")
    all_scores = scores_ref.stream()
    
    total_games = 0
    level_dist = {1: 0, 2: 0, 3: 0}
    recent_activity = {} # fecha -> cuenta
    
    # Ranking para la gráfica de barras
    ranking_data = []

    for doc in all_scores:
        data = doc.to_dict()
        total_games += 1
        
        # Distribución por nivel
        lvl = data.get("nivel", 1)
        level_dist[lvl] = level_dist.get(lvl, 0) + 1
        
        # Actividad reciente (últimos 7 días)
        ts = data.get("timestamp")
        if ts:
            fecha_str = ts.strftime("%Y-%m-%d")
            recent_activity[fecha_str] = recent_activity.get(fecha_str, 0) + 1

    # Preparar Ranking Top 10 (simplificado para la gráfica)
    top_scores = scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in top_scores:
        d = doc.to_dict()
        ranking_data.append({
            "username": d.get("username"),
            "score": d.get("score")
        })

    return {
        "total_players": total_users,
        "total_games": total_games,
        "level_distribution": level_dist,
        "recent_activity": recent_activity,
        "top_ranking": ranking_data
    }
