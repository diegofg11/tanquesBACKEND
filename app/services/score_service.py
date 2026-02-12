import datetime
import jwt
from google.cloud import firestore
from fastapi import HTTPException
from app.schemas.user import ScoreSubmission

SECRET_KEY = "CLAVE_SUPER_SECRETA_TANQUES_BACKEND" # En prod, usar env vars!
ALGORITHM = "HS256"

class ScoreService:
    def __init__(self, db: firestore.Client):
        self.db = db
        self.scores_ref = db.collection("scores")
        self.users_ref = db.collection("users")

    def create_game_token(self, username: str):
        """
        Genera un JWT para una nueva sesión de juego.
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
