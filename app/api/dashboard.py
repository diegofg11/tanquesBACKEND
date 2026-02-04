from fastapi import APIRouter, Depends
from google.cloud import firestore
from app.database import get_db
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def get_dashboard_stats(time_range: str = "all", db: firestore.Client = Depends(get_db)):
    """
    Recupera estadísticas agregadas para el Dashboard con filtros de tiempo.
    """
    # 1. Total Usuarios (Siempre global)
    users_ref = db.collection("users")
    total_users = len(list(users_ref.list_documents()))

    # 2. Configurar Fechas para Filtros (Usar UTC con zona horaria para evitar errores de comparación)
    from datetime import timezone
    now = datetime.now(timezone.utc)
    limit_date = None
    if time_range == "today":
        limit_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == "week":
        limit_date = now - timedelta(days=7)
    
    # 3. Procesar Partidas
    scores_ref = db.collection("scores")
    all_scores = scores_ref.stream()
    
    total_games = 0
    level_dist = {1: 0, 2: 0, 3: 0}
    recent_activity = {} # fecha -> cuenta

    # Inicializar con todas las horas si es "hoy" para que la gráfica se vea completa
    if time_range == "today":
        for h in range(24):
            recent_activity[f"{h:02d}:00"] = 0

    record_of_the_day = 0
    record_in_range = 0
    hoy_date = now.date()

    for doc in all_scores:
        data = doc.to_dict()
        ts = data.get("timestamp")
        
        # Filtro de tiempo: Si hay límite y la partida es anterior, la ignoramos para stats rángo
        is_in_range = True
        if limit_date and ts and ts < limit_date:
            is_in_range = False

        # --- Lógica del Récord de Hoy (Siempre calculada para la tarjeta fija) ---
        if ts and ts.date() == hoy_date:
            score = data.get("score", 0)
            if score > record_of_the_day:
                record_of_the_day = score

        # --- Stats dependientes del Filtro ---
        if is_in_range:
            total_games += 1
            
            # Distribución por nivel
            lvl = data.get("nivel", 1)
            level_dist[lvl] = level_dist.get(lvl, 0) + 1
            
            # Actividad reciente
            if ts:
                if time_range == "today":
                    fecha_str = ts.strftime("%H:00")
                else:
                    fecha_str = ts.strftime("%Y-%m-%d")
                
                recent_activity[fecha_str] = recent_activity.get(fecha_str, 0) + 1
                
                # Récord en el rango seleccionado
                score = data.get("score", 0)
                if score > record_in_range:
                    record_in_range = score

    # 4. Ranking (Top 10 Global - Mantener global para competitividad)
    ranking_data = []
    top_scores = scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in top_scores:
        d = doc.to_dict()
        ranking_data.append({
            "username": d.get("username"),
            "score": d.get("score")
        })

    # 5. Muro de Actividad (Últimos 10 juegos - Siempre últimos)
    live_feed = []
    latest_games = scores_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(10).stream()
    for doc in latest_games:
        d = doc.to_dict()
        ts = d.get("timestamp")
        live_feed.append({
            "username": d.get("username"),
            "score": d.get("score"),
            "nivel": d.get("nivel"),
            "fecha": ts.strftime("%d/%m | %H:%M") if ts else "N/A"
        })

    return {
        "total_players": total_users,
        "total_games": total_games,
        "level_distribution": level_dist,
        "recent_activity": recent_activity,
        "top_ranking": ranking_data,
        "live_feed": live_feed,
        "record_of_the_day": record_of_the_day,
        "record_in_range": record_in_range,
        "active_range": time_range
    }

@router.get("/user/{username}")
def get_user_stats(username: str, db: firestore.Client = Depends(get_db)):
    """
    Busca todas las partidas de un usuario específico y devuelve sus stats.
    """
    scores_ref = db.collection("scores")
    
    try:
        # Intentar varias combinaciones de mayúsculas/minúsculas ya que Firestore es sensible
        variations = [username, username.lower(), username.capitalize(), username.upper()]
        variations = list(dict.fromkeys(variations))
        
        final_user_results = []
        actual_username = username

        for var in variations:
            # Quitamos order_by de la query para evitar el error de "Index missing"
            user_query = scores_ref.where("username", "==", var).stream()
            results = list(user_query)
            if results:
                final_user_results = results
                actual_username = var
                break
        
        if not final_user_results:
            return {"found": False}

        # Convertir a lista de dicts y ordenar por fecha en Python
        games = []
        for doc in final_user_results:
            data = doc.to_dict()
            ts = data.get("timestamp")
            games.append({
                "score": data.get("score", 0),
                "nivel": data.get("nivel", 1),
                "timestamp": ts,
                "fecha": ts.strftime("%d/%m/%Y %H:%M") if ts else "N/A"
            })
        
        # Ordenar: más reciente primero
        games.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min, reverse=True)

        total_score = sum(g["score"] for g in games)
        max_score = max(g["score"] for g in games) if games else 0
        
        levels_count = {1: 0, 2: 0, 3: 0}
        for g in games:
            lvl = g["nivel"]
            if lvl in levels_count:
                levels_count[lvl] += 1

        return {
            "found": True,
            "username": actual_username,
            "total_games": len(games),
            "total_score": total_score,
            "avg_score": round(total_score / len(games), 2),
            "max_score": max_score,
            "level_distribution": levels_count,
            "games": games
        }
    except Exception as e:
        print(f"DEBUG: Error en búsqueda: {str(e)}")
        return {"found": False, "error": str(e)}
