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
    record_of_the_day = 0
    hoy = datetime.utcnow().date()

    for doc in all_scores:
        data = doc.to_dict()
        total_games += 1
        
        # Distribución por nivel
        lvl = data.get("nivel", 1)
        level_dist[lvl] = level_dist.get(lvl, 0) + 1
        
        # Actividad reciente (últimos 7 días) e Histórico del día
        ts = data.get("timestamp")
        if ts:
            fecha_dt = ts.date()
            fecha_str = ts.strftime("%Y-%m-%d")
            recent_activity[fecha_str] = recent_activity.get(fecha_str, 0) + 1
            
            # Récord del día (Punto 2 adelantado un poco en lógica)
            if fecha_dt == hoy:
                score = data.get("score", 0)
                if score > record_of_the_day:
                    record_of_the_day = score

    # 3. Preparar Ranking Top 10
    ranking_data = []
    top_scores = scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in top_scores:
        d = doc.to_dict()
        ranking_data.append({
            "username": d.get("username"),
            "score": d.get("score")
        })

    # 4. Muro de Actividad (Novedad Punto 1: Últimos 10 juegos)
    live_feed = []
    latest_games = scores_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in latest_games:
        d = doc.to_dict()
        ts = d.get("timestamp")
        live_feed.append({
            "username": d.get("username"),
            "score": d.get("score"),
            "nivel": d.get("nivel"),
            "fecha": ts.strftime("%d/%m %H:%M") if ts else "N/A"
        })

    return {
        "total_players": total_users,
        "total_games": total_games,
        "level_distribution": level_dist,
        "recent_activity": recent_activity,
        "top_ranking": ranking_data,
        "live_feed": live_feed,
        "record_of_the_day": record_of_the_day
    }
