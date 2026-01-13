from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

# Esta clase define cómo será nuestra tabla de usuarios en la base de datos SQL.
# Cada atributo de la clase representa una columna de la tabla.
class User(Base):
    __tablename__ = "users" # El nombre de la tabla en el archivo .db

    # 'primary_key=True' significa que este ID es único para cada usuario (como el DNI).
    id = Column(Integer, primary_key=True, index=True)
    
    # 'unique=True' impide que dos personas se registren con el mismo nombre.
    username = Column(String, unique=True, index=True)
    
    # Aquí guardaremos la contraseña. IMPORTANTE: Guardaremos el "hash" (encriptada), nunca el texto real.
    hashed_password = Column(String)
    
    # Esto nos servirá para saber si la cuenta está activa.
    is_active = Column(Boolean, default=True)

    # Puedes añadir más campos aquí, como 'score' o 'level'.
    score = Column(Integer, default=0)
