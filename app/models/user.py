from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

# Aquí me monto mi tabla de usuarios tal cual quiero que sea en mi base de datos SQL.
# Cada cosa que ponga aquí será una columna en mi tabla de verdad.
class User(Base):
    __tablename__ = "users" # Así voy a llamar a mi tabla en el archivo .db

    # Pongo el ID como clave primaria e índice para que sea rapidísimo encontrarlos.
    id = Column(Integer, primary_key=True, index=True)
    
    # El nombre de usuario tiene que ser único; no quiero dos personas llamándose igual.
    username = Column(String, unique=True, index=True)
    
    # IMPORTANTE: Aquí guardo el hash de la contraseña, que no quiero líos si me roban la DB.
    hashed_password = Column(String)
    
    # Con esto controlo si el usuario todavía puede entrar o si le he baneado.
    is_active = Column(Boolean, default=True)

    # Aquí guardo los puntos de cada uno para mi futuro sistema de ránking.
    score = Column(Integer, default=0)
