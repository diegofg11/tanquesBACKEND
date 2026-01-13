from pydantic import BaseModel
from typing import Optional

# Me creo estos 'Schemas' para validar los datos que entran y salen de mi API.
# Son distintos a mis 'Models' porque estos solo me sirven para comprobar formatos.

# Aquí defino lo que le pido a alguien cuando quiera registrarse en mi juego.
class UserCreate(BaseModel):
    username: str
    password: str

# Aquí decido qué datos voy a ENVIAR de vuelta cuando alguien me pregunte por un usuario.
# Lógicamente, NO devuelvo la contraseña por seguridad.
class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool
    score: int

    # Esto lo pongo para que Pydantic sepa leer mis modelos de SQLAlchemy directamente.
    class Config:
        from_attributes = True
