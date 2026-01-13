from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Ruta que me he hecho para registrar a nuevos jugadores.
    - Miro si el nombre ya está pillado.
    - Encripto la contraseña (¡nunca en plano!).
    - Lo guardo en mi base de datos SQL.
    """
    # 1. Primero miro si ya tengo a alguien con ese mismo nombre.
    db_user = db.query(User).filter(User.username == user_data.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este nombre de usuario ya lo tengo registrado"
        )
    
    # 2. Paso la contraseña por mi función de hash para que sea segura.
    hashed_pwd = get_password_hash(user_data.password)
    
    # 3. Monto mi objeto de usuario nuevo.
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_pwd
    )
    
    # 4. Lo mando a la base de datos y hago el commit para confirmar.
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # Le pido a la DB que me devuelva el ID que le ha puesto
    
    return new_user

@router.post("/login")
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Aquí es donde compruebo si alguien puede entrar.
    - Busco al usuario.
    - Verifico que la contraseña me cuadre.
    """
    # 1. Lo busco en mi base de datos por su nombre.
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # 2. Si no lo encuentro o la contraseña no es la suya...
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Me has dado un usuario o contraseña incorrectos"
        )
    
    return {"mensaje": "¡He recordado al usuario! Entrando...", "user_id": user.id}
