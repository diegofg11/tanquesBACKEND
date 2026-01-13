from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import get_password_hash, verify_password

# El APIRouter sirve para agrupar rutas relacionadas (en este caso, todo lo de usuarios).
router = APIRouter(
    prefix="/users",
    tags=["Usuarios"] # Esto agrupa las rutas en la documentación automática (/docs)
)

@router.post("/register", response_model=UserOut)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Ruta para registrar un nuevo jugador.
    - Comprueba si el nombre ya existe.
    - Encripta la contraseña.
    - Guarda al usuario en la base de datos SQL.
    """
    # 1. Buscamos si ya existe alguien con ese nombre
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado"
        )
    
    # 2. Encriptamos la contraseña antes de guardarla
    hashed_pwd = get_password_hash(user_data.password)
    
    # 3. Creamos el objeto del nuevo usuario
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pwd
    )
    
    # 4. Lo añadimos a la base de datos y confirmamos (commit)
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Actualiza el objeto con el ID generado por la base de datos
    
    return new_user

@router.post("/login")
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Ruta básica para iniciar sesión.
    - Busca al usuario.
    - Verifica que la contraseña sea correcta.
    """
    # 1. Buscamos al usuario por su nombre
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # 2. Si no existe o la contraseña no coincide...
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    return {"mensaje": "Inicio de sesión correcto", "user_id": user.id}
