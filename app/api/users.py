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
