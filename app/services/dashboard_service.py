from google.cloud import firestore
from datetime import datetime, timedelta, timezone

class DashboardService:
    def __init__(self, db: firestore.Client):
        self.db = db
        self.users_ref = db.collection("users")
        self.scores_ref = db.collection("scores")

    def get_global_stats(self, time_range: str = "all"):
        """
        Genera estadísticas completas para el dashboard administrativo.
        """
        # 1. Total Usuarios
        total_users = len(list(self.users_ref.list_documents()))

        # 2. Configurar Filtros
        now = datetime.now(timezone.utc)
        limit_date = None
        if time_range == "today":
            limit_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == "week":
            limit_date = now - timedelta(days=7)
        
        # 3. Procesar Partidas
        all_scores = self.scores_ref.stream()
        
        total_games = 0
        level_dist = {1: 0, 2: 0, 3: 0}
        recent_activity = {}
        
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
            username = data.get("username", "Anon")
            score = data.get("score", 0)

            # Record del día (Siempre visible)
            if ts and ts.date() == hoy_date:
                if score > record_of_the_day:
                    record_of_the_day = score
                    record_of_the_day_user = username

            # Filtrado temporal
            if limit_date and ts and ts < limit_date:
                continue

            total_games += 1
            
            # Distribución Nivel
            lvl = data.get("nivel", 1)
            level_dist[lvl] = level_dist.get(lvl, 0) + 1
            
            # Actividad
            if ts:
                k = ts.strftime("%H:00") if time_range == "today" else ts.strftime("%Y-%m-%d")
                recent_activity[k] = recent_activity.get(k, 0) + 1

            # Récord en rango
            if score > record_in_range:
                record_in_range = score
                record_in_range_user = username

        # 4. Top Ranking & Live Feed
        top_ranking = self._get_ranking(10)
        live_feed = self._get_live_feed(10)

        return {
            "total_players": total_users,
            "total_games": total_games,
            "level_distribution": level_dist,
            "recent_activity": recent_activity,
            "top_ranking": top_ranking,
            "live_feed": live_feed,
            "record_of_the_day": record_of_the_day,
            "record_of_the_day_user": record_of_the_day_user,
            "record_in_range": record_in_range,
            "record_in_range_user": record_in_range_user,
            "active_range": time_range
        }

    def get_user_stats(self, username: str):
        """
        Busca usuario o estadísticas sueltas.
        """
        # Intentar varias capitalizaciones
        variations = list({username, username.lower(), username.capitalize(), username.upper()})
        
        target_username = None
        
        # Buscar en Usuarios
        for var in variations:
            if self.users_ref.document(var).get().exists:
                target_username = var
                break
        
        # Buscar en Scores
        if not target_username:
            for var in variations:
                if list(self.scores_ref.where("username", "==", var).limit(1).stream()):
                    target_username = var
                    break
        
        if not target_username:
            return {"found": False}

        # Calcular Estadísticas
        games_query = self.scores_ref.where("username", "==", target_username).stream()
        games = []
        for doc in games_query:
            d = doc.to_dict()
            ts = d.get("timestamp")
            games.append({
                "score": d.get("score", 0),
                "nivel": d.get("nivel", 1),
                "timestamp": ts,
                "fecha": ts.strftime("%d/%m/%Y %H:%M") if ts else "N/A"
            })
        
        games.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min, reverse=True)
        
        total_score = sum(g["score"] for g in games)
        
        return {
            "found": True,
            "username": target_username,
            "total_games": len(games),
            "total_score": total_score,
            "avg_score": round(total_score / len(games), 2) if games else 0,
            "max_score": max(g["score"] for g in games) if games else 0,
            "games": games
        }

    def _get_ranking(self, limit):
        query = self.scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [{"username": d.to_dict().get("username"), "score": d.to_dict().get("score")} for d in query]

    def _get_live_feed(self, limit):
        query = self.scores_ref.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
        feed = []
        for doc in query:
            d = doc.to_dict()
            ts = d.get("timestamp")
            feed.append({
                "username": d.get("username"),
                "score": d.get("score"),
                "nivel": d.get("nivel"),
                "fecha": ts.strftime("%d/%m | %H:%M") if ts else "N/A"
            })
        return feed
