from pydantic import BaseModel
from typing import Optional

# Los 'Schemas' (también llamados DTOs) sirven para validar los datos que entran y salen de nuestra API.
# A diferencia de los 'Models', estos no guardan datos en la DB, solo comprueban que el formato es correcto.

# Este esquema define qué datos necesitamos cuando alguien se registra.
class UserCreate(BaseModel):
    username: str
    password: str

# Este esquema define qué datos vamos a DEVOLVER cuando alguien consulte un usuario.
# Fíjate que NO devolvemos la contraseña por seguridad.
class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    score: int

    # Esta línea permite que Pydantic lea datos directamente de modelos de SQLAlchemy.
    class Config:
        from_attributes = True
