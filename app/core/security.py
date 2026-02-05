"""
Utilidades de seguridad para el hash y verificación de contraseñas.

Utiliza passlib con el esquema pbkdf2_sha256 para garantizar un almacenamiento
seguro de las credenciales de los usuarios.
"""
from passlib.context import CryptContext

# Configuración del contexto de criptografía.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Verifica si una contraseña en texto plano coincide con su hash almacenado.
    
    Args:
        plain_password (str): La contraseña proporcionada por el usuario.
        hashed_password (str): El hash guardado en la base de datos.
        
    Returns:
        bool: True si coinciden, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Genera un hash seguro a partir de una contraseña en texto plano.
    
    Args:
        password (str): La contraseña a encriptar.
        
    Returns:
        str: El hash resultante para ser almacenado.
    """
    return pwd_context.hash(password)
