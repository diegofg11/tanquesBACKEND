"""
Rutas de la API para la gestión de usuarios y puntuaciones.

Este módulo implementa el registro, autenticación, gestión de sesiones de juego
y el sistema de puntuaciones (Leaderboard).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import firestore
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, ScoreSubmission, UserProfileOut
from app.core.security import get_password_hash, verify_password
import jwt
import datetime

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

# --- SEGURIDAD: CONFIGURACIÓN JWT SIMPLIFICADA ---
SECRET_KEY = "CLAVE_SUPER_SECRETA_TANQUES_BACKEND" # En prod, usar env vars!
ALGORITHM = "HS256"

@router.post("/register", response_model=UserOut)
def register_user(user_data: UserCreate, db: firestore.Client = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema.
    
    Verifica que el nombre de usuario no esté en uso. Encripta la contraseña
    antes de guardarla en Firestore.
    
    Args:
        user_data (UserCreate): El nombre de usuario y la contraseña deseados.
        db (firestore.Client): Cliente de base de datos inyectado.
        
    Returns:
        UserOut: Los datos del usuario recién creado.
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
    Autentica a un usuario.
    
    Compara las credenciales proporcionadas con los datos almacenados en Firestore.
    
    Args:
        user_data (UserCreate): Credenciales enviadas por el usuario.
        db (firestore.Client): Cliente de base de datos.
        
    Returns:
        dict: Mensaje de éxito y el nombre de usuario si la autenticación es válida.
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

@router.post("/{username}/start-game")
def start_game(username: str, db: firestore.Client = Depends(get_db)):
    """
    Inicia una sesión de juego segura.
    
    Genera un TOKEN DE PARTIDA (JWT) válido por 10 minutos. Este token es 
    obligatorio para enviar puntuaciones al finalizar la partida.
    
    Args:
        username (str): El nombre de usuario que inicia la partida.
        
    Returns:
        dict: El token de sesión generado.
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
    Calcula, valida y guarda la puntuación de una partida finalizada.
    
    Requiere un game_token válido generado previamente por /start-game.
    Calcula la puntuación final basada en el nivel, tiempo y daño recibido.
    Actualiza el récord personal del usuario si es necesario.
    
    Args:
        username (str): Nombre del usuario que envía el score.
        stats (ScoreSubmission): Estadísticas de la partida y token de sesión.
        
    Returns:
        dict: Puntuación de la partida, si es nuevo récord y el récord actual.
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

    # 4. Actualizar usuario (Mejor Puntuación - LOGICA AUTO-REPARADORA)
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    
    titulo_record = False
    
    # Buscamos el verdadero MAX histórico de este usuario en 'scores'
    scores_query = scores_ref.where("username", "==", username).stream()
    
    true_max_score = 0
    for s_doc in scores_query:
        s_data = s_doc.to_dict()
        val = s_data.get("score", 0)
        if val > true_max_score:
            true_max_score = val

    # Actualizamos el perfil si es necesario
    if user_doc.exists:
        stored_score = user_doc.to_dict().get("score", 0)
        
        # Si el score actual supera al histórico (caso normal de récord)
        if score_final > stored_score:
            titulo_record = True
        
        # Sincronización: Si el verdadero max es mayor que lo guardado, actualizamos
        if true_max_score > stored_score:
            user_ref.update({"score": true_max_score})
            
    return {
        "score_partida": score_final,
        "nuevo_record": titulo_record,
        "high_score_actual": true_max_score # Devolvemos siempre la verdad
    }

@router.get("/ranking/top")
def get_top_scores(db: firestore.Client = Depends(get_db)):
    """
    Obtiene el Top 10 global de puntuaciones individuales.
    
    Retorna una lista de los 10 mejores resultados registrados en el sistema,
    permitiendo que un mismo usuario aparezca varias veces si tiene múltiples
    puntuaciones altas.
    
    Returns:
        list: Lista de diccionarios con username, score y fecha.
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

@router.get("/{username}", response_model=UserProfileOut)
def get_user_profile(username: str, db: firestore.Client = Depends(get_db)):
    """
    Recupera el perfil completo de un usuario.
    
    Incluye datos básicos del usuario, estadísticas globales y un historial
    de las últimas 5 partidas realizadas.
    
    Args:
        username (str): El nombre del usuario a consultar.
        
    Returns:
        UserProfileOut: Objeto complejo con toda la información del perfil.
    """
    # 1. Datos Usuario
    doc_ref = db.collection("users").document(username)
    doc = doc_ref.get()
    
    if not doc.exists:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")
         
    user_data = doc.to_dict()
    
    # 2. Historial de Partidas (Últimas 5)
    scores_ref = db.collection("scores")
    all_scores_stream = scores_ref.where("username", "==", username).stream()
    
    all_scores = []
    for s in all_scores_stream:
        d = s.to_dict()
        # Convertir timestamp a string legible
        ts = d.get("timestamp")
        fecha_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "N/A"
        
        all_scores.append({
            "score": d.get("score", 0),
            "nivel": d.get("nivel", 1),
            "fecha": fecha_str,
            "_dt": ts # Temporal para ordenar
        })
        
    # Ordenar por fecha descendente
    all_scores.sort(key=lambda x: x["_dt"], reverse=True)
    
    # 3. Datos Finales
    total_games = len(all_scores)
    history_5 = all_scores[:5] # Top 5 recientes
    
    # Limpiamos el campo temporal _dt
    for h in history_5:
        del h["_dt"]

    return {
        **user_data,
        "total_games": total_games,
        "history": history_5
    }
