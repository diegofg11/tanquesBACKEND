"""
Configuración de la conexión con Firebase Firestore.
Inicializa el SDK de Admin y provee la dependencia de base de datos.
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Ruta al archivo de credenciales de servicio.
# Se espera que 'firebase-key.json' esté en la raíz del proyecto.
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase-key.json")

# Inicialización del SDK de Firebase.
# Se verifica si ya existe una app inicializada para evitar errores en recargas.
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(JSON_PATH)
        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"ERROR CRÍTICO AL INICIAR FIREBASE: {e}")
    print("Asegúrate de que 'firebase-key.json' esté en la carpeta raíz.")

# Cliente de Firestore global.
db_firestore = firestore.client()

def get_db():
    """
    Dependencia de FastAPI que yielda el cliente de Firestore.
    """
    yield db_firestore
