from fastapi import APIRouter, Depends, HTTPException, status
from google.cloud import firestore
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash, verify_password

# Me creo este APIRouter para tener todas las rutas de mis usuarios bien agrupadas.
router = APIRouter(
    prefix="/users",
    tags=["Usuarios"] # Así me salen juntitos en la documentación (/docs)
)

@router.post("/register", response_model=UserOut)
def register_user(user_data: UserCreate, db: firestore.Client = Depends(get_db)):
    """
    Ruta que me he hecho para registrar a nuevos jugadores.
    - Miro si el nombre ya está pillado en Firestore.
    - Encripto la contraseña.
    - Lo guardo como un documento en la colección "users".
    """
    # 1. Busco si ya existe un documento con ese username
    users_ref = db.collection("users")
    query = users_ref.where("username", "==", user_data.username).limit(1).get()
    
    if len(query) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este nombre de usuario ya lo tengo registrado en la nube"
        )
    
    # 2. Encripto la contraseña
    hashed_pwd = get_password_hash(user_data.password)
    
    # 3. Monto el objeto y lo convierto a diccionario
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pwd
    )
    
    # 4. Lo guardo en Firestore. 
    # Uso el username como ID del documento para que sea único por naturaleza.
    users_ref.document(user_data.username).set(new_user.to_dict())
    
    return new_user

@router.post("/login")
def login(user_data: UserCreate, db: firestore.Client = Depends(get_db)):
    """
    Aquí es donde compruebo si alguien puede entrar desde Firebase.
    """
    # 1. Intento traer el documento que tiene ese username como ID
    user_doc = db.collection("users").document(user_data.username).get()
    
    # 2. Si no existe o la contraseña no cuadra...
    if not user_doc.exists:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No encuentro a ese usuario en mi base de datos de Firebase"
        )
    
    user_data_db = user_doc.to_dict()
    
    if not verify_password(user_data.password, user_data_db["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La contraseña no coincide"
        )
    
    return {"mensaje": "¡Usuario verificado en Firebase!", "username": user_data.username}

@router.post("/{username}/submit-score")
def submit_score(username: str, stats: ScoreSubmission, db: firestore.Client = Depends(get_db)):
    """
    Endpoint para enviar las estadísticas de una partida y calcular la puntuación.
    Fórmula: Puntos_Base - (Tiempo * 2) - (Daño * 5)
    """
    # 1. Definimos los puntos base según el nivel alcanzado
    puntos_base = 0
    if stats.nivel_alcanzado == 1:
        puntos_base = 1000
    elif stats.nivel_alcanzado == 2:
        puntos_base = 3000
    elif stats.nivel_alcanzado == 3:
        puntos_base = 6000 # Victoria, el máximo base posible
    
    # 2. Aplicamos la fórmula de penalización
    # Restamos 2 puntos por cada segundo y 5 puntos por cada punto de daño recibido.
    penalizacion_tiempo = stats.tiempo_segundos * 2
    penalizacion_daño = stats.daño_recibido * 5
    
    score_final = puntos_base - penalizacion_tiempo - penalizacion_daño
    
    # Evitamos puntuaciones negativas, queda feo.
    if score_final < 0:
        score_final = 0
        
    # 3. Busco al usuario en Firestore
    user_ref = db.collection("users").document(username)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    user_data = user_doc.to_dict()
    current_high_score = user_data.get("score", 0)
    
    # 4. Solo actualizo si ha superado su récord personal
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
    Devuelve los 10 mejores jugadores ordenados por puntuación.
    """
    users_ref = db.collection("users")
    
    # Hago la query a Firestore: Ordenar por 'score' descendente y pillar 10
    query = users_ref.order_by("score", direction=firestore.Query.DESCENDING).limit(10).stream()
    
    ranking = []
    for doc in query:
        data = doc.to_dict()
        ranking.append({
            "username": data.get("username"),
            "score": data.get("score", 0)
        })
        
    return ranking
