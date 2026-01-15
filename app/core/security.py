"""
Utilidades de seguridad para el hash y verificación de contraseñas.
"""
from passlib.context import CryptContext

# Configuración del contexto de criptografía.
# Se utiliza el esquema pbkdf2_sha256.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Me he hecho esta función para comparar la contraseña que me escriben
    con el churro encriptado (hash) que tengo guardado.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Con esto paso la contraseña de texto plano a un hash que nadie pueda leer.
    Así si me roban la base de datos, no verán las contraseñas reales.
    """
    return pwd_context.hash(password)
