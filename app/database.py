"""
Configuración de la conexión con Firebase Firestore.
Inicializa el SDK de Admin y provee la dependencia de base de datos.
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Nombre de la variable de entorno que contendrá el JSON en la nube
ENV_VAR_NAME = "FIREBASE_CREDENTIALS"

# Ruta al archivo local (solo para desarrollo)
JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase-key.json")

try:
    if not firebase_admin._apps:
        cred = None
        
        # 1. Intentamos leer de la Variable de Entorno (Prioridad Nube)
        env_json = os.getenv(ENV_VAR_NAME)
        if env_json:
            # Parseamos el string JSON a un diccionario
            cred_dict = json.loads(env_json)
            cred = credentials.Certificate(cred_dict)
            print("INFO: Credenciales cargadas desde Variable de Entorno.")
        
        # 2. Si no, intentamos leer del archivo local (Prioridad Local)
        elif os.path.exists(JSON_PATH):
            cred = credentials.Certificate(JSON_PATH)
            print(f"INFO: Credenciales cargadas desde archivo local: {JSON_PATH}")
            
        else:
            raise FileNotFoundError("No se encontraron credenciales válidas (ni ENV ni Archivo).")

        firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"ERROR CRÍTICO AL INICIAR FIREBASE: {e}")
    # En local permitimos fallar, pero en la nube saltará error
    pass

# Cliente de Firestore global.
db_firestore = firestore.client()

def get_db():
    """
    Dependencia de FastAPI que yielda el cliente de Firestore.
    """
    yield db_firestore
