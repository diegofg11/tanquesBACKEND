"""
Rutas de la API para el Dashboard administrativo.

Este módulo proporciona estadísticas agregadas, distribución de niveles,
actividad reciente y utilidades de búsqueda de usuarios para la interfaz web.
"""
from fastapi import APIRouter, Depends
from google.cloud import firestore
from app.database import get_db
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)

@router.get("/stats")
def get_dashboard_stats(time_range: str = "all", db: firestore.Client = Depends(get_db)):
    """
    Recupera estadísticas globales y filtradas para el panel principal.
    
    Calcula el total de jugadores, partidas jugadas, distribución por niveles
    y datos para las gráficas de actividad.
    
    Args:
        time_range (str): Filtro temporal ("all", "today", "week"). Por defecto "all".
        db (firestore.Client): Cliente de Firestore.
        
    Returns:
        dict: Un objeto con todas las métricas necesarias para el Dashboard.
    """
    # 1. Total Usuarios (Siempre global)
    users_ref = db.collection("users")
    total_users = len(list(users_ref.list_documents()))

    # 2. Configurar Fechas para Filtros (Usar UTC con zona horaria para evitar errores de comparación)
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
    record_of_the_day_user = "---"
    record_in_range = 0
    record_in_range_user = "---"
    hoy_date = now.date()

    for doc in all_scores:
        data = doc.to_dict()
        ts = data.get("timestamp")
        username_score = data.get("username", "Anon")
        
        # Filtro de tiempo: Si hay límite y la partida es anterior, la ignoramos para stats rángo
        is_in_range = True
        if limit_date and ts and ts < limit_date:
            is_in_range = False

        # --- Lógica del Récord de Hoy (Siempre calculada para la tarjeta fija) ---
        if ts and ts.date() == hoy_date:
            score = data.get("score", 0)
            if score > record_of_the_day:
                record_of_the_day = score
                record_of_the_day_user = username_score

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
                    record_in_range_user = username_score

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
        "record_of_the_day_user": record_of_the_day_user,
        "record_in_range": record_in_range,
        "record_in_range_user": record_in_range_user,
        "active_range": time_range
    }

@router.get("/user/{username}")
def get_user_stats(username: str, db: firestore.Client = Depends(get_db)):
    """
    Busca estadísticas detalladas y el historial de un usuario específico.
    
    Realiza una búsqueda flexible (ignorando mayúsculas) y retorna todas las
    partidas registradas para ese usuario con cálculos de promedio y máximos.
    
    Args:
        username (str): El nombre de usuario a buscar.
        
    Returns:
        dict: Datos de rendimiento del usuario o indicación de que no existe.
    """
    scores_ref = db.collection("scores")
    
    try:
        # 1. Intentar encontrar al usuario en la colección 'users' primero
        users_ref = db.collection("users")
        variations = [username, username.lower(), username.capitalize(), username.upper()]
        variations = list(dict.fromkeys(variations))
        
        target_user = None
        actual_username = username

        # Buscar en 'users' (ID del documento es el username)
        for var in variations:
            user_doc = users_ref.document(var).get()
            if user_doc.exists:
                target_user = user_doc
                actual_username = var
                break
        
        # Si no está en 'users', probamos a ver si hay algo en 'scores' con ese nombre
        if not target_user:
            for var in variations:
                first_score = list(scores_ref.where("username", "==", var).limit(1).stream())
                if first_score:
                    actual_username = var
                    break
            else:
                # Si no está en niguno, no existe
                return {"found": False}

        # 2. Buscar partidas en 'scores'
        user_query = scores_ref.where("username", "==", actual_username).stream()
        results = list(user_query)
        
        # Convertir a lista de dicts y ordenar por fecha en Python
        games = []
        for doc in results:
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
            "avg_score": round(total_score / len(games), 2) if games else 0,
            "max_score": max_score,
            "level_distribution": levels_count,
            "games": games
        }
    except Exception as e:
        print(f"DEBUG: Error en búsqueda: {str(e)}")
        return {"found": False, "error": str(e)}
