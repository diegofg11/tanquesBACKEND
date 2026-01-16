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

# --- SEGURIDAD: CONFIGURACIÓN JWT SIMPLIFICADA ---
SECRET_KEY = "CLAVE_SUPER_SECRETA_TANQUES_BACKEND" # En prod, usar env vars!
ALGORITHM = "HS256"
import jwt
import datetime

@router.post("/{username}/start-game")
def start_game(username: str, db: firestore.Client = Depends(get_db)):
    """
    Genera un TOKEN DE PARTIDA válido por 10 minutos.
    Unity debe llamar a esto al empezar la partida y guardar el token.
    """
    # Verificar usuario
    user_doc = db.collection("users").document(username).get()
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Crear Token
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    payload = {
        "sub": username,
        "type": "game_session",
        "exp": expiration
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"game_token": token}

@router.post("/{username}/submit-score")
def submit_score(username: str, stats: ScoreSubmission, db: firestore.Client = Depends(get_db)):
    """
    Calcula y guarda la puntuación. REQUIERE game_token válido.
    """
    # 0. VERIFICACIÓN DE SEGURIDAD (ANTI-TRAMPAS)
    if not stats.game_token:
         raise HTTPException(status_code=403, detail="Falta el token de partida. ¿Hiciste Start Game?")
    
    try:
        payload = jwt.decode(stats.game_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != username:
            raise HTTPException(status_code=403, detail="El token no pertenece a este usuario")
        if payload.get("type") != "game_session":
            raise HTTPException(status_code=403, detail="Token inválido para enviar scores")
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="La partida ha caducado (Token expirado)")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Token inválido o manipulado")

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

    # 3. Guardar en la colección 'scores'
    scores_ref = db.collection("scores")
    new_score_doc = scores_ref.document()
    
    score_data = {
        "username": username,
        "score": score_final,
        "nivel": stats.nivel_alcanzado,
        "timestamp": datetime.datetime.utcnow()
    }
    
    new_score_doc.set(score_data)

    # 4. Actualizar usuario (Mejor Puntuación)
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    
    titulo_record = False
    
    if user_doc.exists:
        current_best = user_doc.to_dict().get("score", 0)
        if score_final > current_best:
            user_ref.update({"score": score_final})
            titulo_record = True
            current_best = score_final
    else:
        pass
        
    return {
        "score_partida": score_final,
        "nuevo_record": titulo_record,
        "high_score_actual": score_final
    }

@router.get("/ranking/top")
def get_top_scores(db: firestore.Client = Depends(get_db)):
    """
    Recupera el Top 10 de PUNTUACIONES (Partidas) globales.
    Puede haber múltiples entradas del mismo usuario si ha jugado muy bien varias veces.
    """
    scores_ref = db.collection("scores")
    
    # Ordenamos por score descendente
    query = scores_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    ranking = []
    for doc in query:
        data = doc.to_dict()
        ranking.append({
            "username": data.get("username"),
            "score": data.get("score", 0),
            "fecha": data.get("timestamp") # Opcional: para mostrar cuándo fue
        })
        
    return ranking

@router.get("/{username}", response_model=UserOut)
def get_user_profile(username: str, db: firestore.Client = Depends(get_db)):
    """
    Obtiene los datos públicos de un usuario (para el Menú Principal).
    """
    doc_ref = db.collection("users").document(username)
    doc = doc_ref.get()
    
    if not doc.exists:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")
         
    return doc.to_dict()
