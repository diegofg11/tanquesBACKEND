"""
Rutas de la API para gestión de usuarios y puntuaciones.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import firestore
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, ScoreSubmission
from app.core.security import get_password_hash, verify_password

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

@router.post("/register", response_model=UserOut)
def register_user(user_data: UserCreate, db: firestore.Client = Depends(get_db)):
    """
    Registra un nuevo usuario en Firestore.
    Verifica que el nombre de usuario no exista previamente.
    """
    # 1. Verificar existencia del usuario
    users_ref = db.collection("users")
    query = users_ref.where("username", "==", user_data.username).limit(1).get()
    
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
    
    # 4. Guardado en Firestore (username es el ID del documento)
    users_ref.document(user_data.username).set(new_user.to_dict())
    
    return new_user

@router.post("/login")
def login(user_data: UserCreate, db: firestore.Client = Depends(get_db)):
    """
    Autentica a un usuario verificando sus credenciales contra Firestore.
    """
    # 1. Recuperar documento del usuario
    user_doc = db.collection("users").document(user_data.username).get()
    
    # 2. Verificar existencia y contraseña
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
    
    return {"mensaje": "Autenticación exitosa", "username": user_data.username}

@router.post("/{username}/submit-score")
def submit_score(username: str, stats: ScoreSubmission, db: firestore.Client = Depends(get_db)):
    """
    Calcula y actualiza la puntuación del usuario si supera su récord personal.
    Fórmula: Puntos_Base - (Tiempo * 2) - (Daño * 5)
    """
    # 1. Definir puntos base según nivel
    puntos_base = 0
    if stats.nivel_alcanzado == 1:
        puntos_base = 1000
    elif stats.nivel_alcanzado == 2:
        puntos_base = 3000
    elif stats.nivel_alcanzado == 3:
        puntos_base = 6000
    
    # 2. Calcular penalizaciones
    penalizacion_tiempo = stats.tiempo_segundos * 2
    penalizacion_daño = stats.daño_recibido * 5
    
    score_final = puntos_base - penalizacion_tiempo - penalizacion_daño
    
    if score_final < 0:
        score_final = 0
        
    # 3. Recuperar usuario
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    user_data = user_doc.to_dict()
    current_high_score = user_data.get("score", 0)
    
    # 4. Actualizar si es nuevo récord
    nuevo_record = False
    if score_final > current_high_score:
        user_ref.update({"score": score_final})
        nuevo_record = True
        
    return {
        "score_partida": score_final,
        "nuevo_record": nuevo_record,
        "high_score_actual": max(score_final, current_high_score)
    }

@router.get("/ranking/top")
def get_top_scores(db: firestore.Client = Depends(get_db)):
    """
    Recupera el Top 10 de usuarios ordenados por puntuación descendente.
    """
    users_ref = db.collection("users")
    
    query = users_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    ranking = []
    for doc in query:
        data = doc.to_dict()
        ranking.append({
            "username": data.get("username"),
            "score": data.get("score", 0)
        })
        
    return ranking
