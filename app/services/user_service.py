from google.cloud import firestore
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

class UserService:
    def __init__(self, db: firestore.Client):
        self.db = db
        self.users_ref = db.collection("users")
        self.scores_ref = db.collection("scores")

    def register_user(self, user_data: UserCreate):
        """
        Registra un nuevo usuario en el sistema.
        """
        # 1. Verificar existencia del usuario
        query = self.users_ref.where("username", "==", user_data.username).limit(1).get()
        
        if len(query) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este nombre de usuario ya está registrado."
            )
        
        # 2. Hashing de contraseña
        hashed_pwd = get_password_hash(user_data.password)
        
        # 3. Creación del objeto User
        new_user = User(
            username=user_data.username,
            hashed_password=hashed_pwd
        )
        
        # 4. Guardado en Firestore
        self.users_ref.document(user_data.username).set(new_user.to_dict())
        
        return new_user

    def authenticate_user(self, user_data: UserCreate):
        """
        Verifica credenciales de usuario.
        """
        user_doc = self.users_ref.document(user_data.username).get()
        
        if not user_doc.exists:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado."
            )
        
        user_data_db = user_doc.to_dict()
        
        if not verify_password(user_data.password, user_data_db["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta."
            )
        
        return user_data_db

    def get_user_profile(self, username: str):
        """
        Obtiene el perfil completo y estadísticas del usuario.
        """
        doc = self.users_ref.document(username).get()
        
        if not doc.exists:
             raise HTTPException(status_code=404, detail="Usuario no encontrado")
             
        user_data = doc.to_dict()
        
        # Historial de Partidas (Últimas 5)
        all_scores_stream = self.scores_ref.where("username", "==", username).stream()
        
        all_scores = []
        for s in all_scores_stream:
            d = s.to_dict()
            ts = d.get("timestamp")
            fecha_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "N/A"
            
            all_scores.append({
                "score": d.get("score", 0),
                "nivel": d.get("nivel", 1),
                "fecha": fecha_str,
                "_dt": ts
            })
            
        all_scores.sort(key=lambda x: x["_dt"], reverse=True)
        
        total_games = len(all_scores)
        history_5 = all_scores[:5]
        
        for h in history_5:
            del h["_dt"]

        return {
            **user_data,
            "total_games": total_games,
            "history": history_5
        }
