from passlib.context import CryptContext

# 1. Configuramos el contexto de encriptación.
# Usamos 'pbkdf2_sha256' por compatibilidad con Python 3.13 en Windows.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Compara una contraseña en texto plano (la que escribe el usuario al loguearse)
    con el hash guardado en la base de datos.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Transforma una contraseña de texto plano en un "hash" ilegible.
    Ejemplo: "1234" -> "$2b$12$EixZaYVK1upzZ..."
    """
    return pwd_context.hash(password)
