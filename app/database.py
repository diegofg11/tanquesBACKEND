import firebase_admin
from firebase_admin import credentials, firestore
import os

# 1. Busco mi llave de Firebase (el archivo .json que te has bajado)
# Asumo que se llama 'firebase-key.json' y está en la raíz del proyecto.
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase-key.json")

# 2. Inicializo el SDK de Firebase.
# Solo lo hago si no se ha inicializado ya (para evitar errores al hacer hot-reload).
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(JSON_PATH)
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"ERROR CRÍTICO AL INICIAR FIREBASE: {e}")
    print("Asegúrate de que 'firebase-key.json' esté en la carpeta raíz.")

# 3. Me preparo mi cliente de Firestore.
db_firestore = firestore.client()

# Esta función la mantengo para que el resto del código siga funcionando casi igual.
# Ahora en lugar de una sesión de SQL, inyectará el cliente de Firestore.
def get_db():
    """
    Proporciona el cliente de Firestore para las peticiones.
    """
    yield db_firestore
