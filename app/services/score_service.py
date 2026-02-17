"""
Servicio de Puntuaciones y Sesiones de Juego.

Gestiona la creación de tokens de sesión, validación de partidas y
el procesamiento de puntuaciones finales, incluyendo detección básica de trampas.
"""
import datetime
import jwt
from typing import List, Dict, Any
from google.cloud import firestore
from fastapi import HTTPException
from app.schemas.user import ScoreSubmission
from app.core.logger import get_logger

logger = get_logger("app.services.score")
SECRET_KEY = "CLAVE_SUPER_SECRETA_TANQUES_BACKEND" # TODO: Mover a variables de entorno
ALGORITHM = "HS256"

class ScoreService:
    """
    Servicio para lógica de puntuaciones y sesiones.
    """
    def __init__(self, db: firestore.Client):
        self.db = db
        self.scores_ref = db.collection("scores")
        self.users_ref = db.collection("users")

    def create_game_token(self, username: str) -> str:
        """
        Genera un JWT para una nueva sesión de juego.
        
        El token tiene una validez limitada y firma la sesión del usuario.
        """
        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        payload = {
            "sub": username,
            "type": "game_session",
            "exp": expiration
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def validate_game_token(self, token: str, username: str):
        """
        Valida que el token pertenezca al usuario y sea de tipo juego.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("sub") != username:
                raise HTTPException(status_code=403, detail="El token no pertenece a este usuario")
            if payload.get("type") != "game_session":
                raise HTTPException(status_code=403, detail="Token inválido para enviar scores")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="La partida ha caducado (Token expirado)")
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Token inválido o manipulado")

            raise HTTPException(status_code=403, detail="Token inválido o manipulado")

    def _sanity_check(self, stats: ScoreSubmission, username: str):
        """
        Detecta anomalías o trampas obvias en los datos.
        """
        # Reglas de negocio (tiempos mínimos imposibles)
        min_seconds_map = {1: 5, 2: 15, 3: 30}
        min_sec = min_seconds_map.get(stats.nivel_alcanzado, 5)

        if stats.tiempo_segundos < min_sec:
            logger.warning(f"CHEAT DETECTED: {username} completó Nivel {stats.nivel_alcanzado} en {stats.tiempo_segundos}s (Min: {min_sec}s)")
            # Podríamos lanzar error, o shadowbanear. Por ahora, forzamos tiempo mínimo para penalizar score.
            stats.tiempo_segundos = min_sec * 2 # Penalización doble

    def calculate_score(self, stats: ScoreSubmission):
        """
        Calcula la puntuación basada en reglas de negocio.
        """
        puntos_base = {1: 1000, 2: 3000, 3: 6000}.get(stats.nivel_alcanzado, 0)
        
        penalizacion_tiempo = stats.tiempo_segundos * 2
        penalizacion_daño = stats.daño_recibido * 5
        
        score_final = puntos_base - penalizacion_tiempo - penalizacion_daño
        return max(0, score_final)

    def submit_score(self, username: str, stats: ScoreSubmission):
        """
        Procesa el envío de una puntuación final.
        """
        # 1. Validar Token
        self.validate_game_token(stats.game_token, username)
        
        # 1.5 Sanity Check (Validar integridad)
        self._sanity_check(stats, username)

        logger.info(f"Procesando Score para {username}: Nivel {stats.nivel_alcanzado}, Tiempo {stats.tiempo_segundos}s")

        # 2. Calcular Score
        score_final = self.calculate_score(stats)

        # 3. Guardar Score
        score_data = {
            "username": username,
            "score": score_final,
            "nivel": stats.nivel_alcanzado,
            "timestamp": datetime.datetime.utcnow()
        }
        self.scores_ref.document().set(score_data)

        # 4. Actualizar Récord de Usuario
        return self._update_user_high_score(username, score_final)

    def _update_user_high_score(self, username: str, new_score: int):
        """
        Verifica y actualiza el high score del usuario si es necesario.
        """
        user_doc_ref = self.users_ref.document(username)
        user_snap = user_doc_ref.get()
        
        titulo_record = False
        true_max_score = 0

        # Calcular MAX real desde la colección scores (source of truth)
        scores_query = self.scores_ref.where("username", "==", username).stream()
        for s in scores_query:
            val = s.to_dict().get("score", 0)
            if val > true_max_score:
                true_max_score = val

        if user_snap.exists:
            stored_score = user_snap.to_dict().get("score", 0)
            if new_score > stored_score:
                titulo_record = True
            
            if true_max_score > stored_score:
                user_doc_ref.update({"score": true_max_score})
                logger.info(f"Nuevo Récord Global para {username}: {true_max_score}")
        
        return {
            "score_partida": new_score,
            "nuevo_record": titulo_record,
            "high_score_actual": true_max_score
        }

    def get_top_ranking(self, limit: int = 10):
        """
        Obtiene el top global de puntuaciones.
        """
        query = self.scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(limit).stream()
        
        ranking = []
        for doc in query:
            data = doc.to_dict()
            ranking.append({
                "username": data.get("username"),
                "score": data.get("score", 0),
                "fecha": data.get("timestamp")
            })
        return ranking
