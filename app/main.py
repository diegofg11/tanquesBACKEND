from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from google.cloud import firestore

# Mis archivos locales
from app.api import users
from app.api.game import manager
from app.database import get_db
from app.models.user import User
from app.schemas.game import TankState

# --- MI INSTANCIA PRINCIPAL ---
app = FastAPI(
    title="Tanques API",
    description="Backend para mi juego de tanques con Firebase Firestore",
    version="0.2.0"
)

# ME DOY PERMISOS DE CORS:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Aquí conecto mis rutas de usuarios
app.include_router(users.router)

# --- MIS MANEJADORES DE ERRORES ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "He detectado un error de validación", "detalle": exc.errors()},
    )

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Ha petado algo interno", "detalle": str(exc)},
    )

@app.get("/")
async def root():
    return {
        "mensaje": "¡Mi API de Tanques con Firebase está en marcha!",
        "doc_url": "/docs"
    }

# --- MI LÓGICA DE WEBSOCKETS (CON VERIFICACIÓN DE FIREBASE) ---

@app.websocket("/ws/game/{room_id}/{username}")
async def game_websocket(websocket: WebSocket, room_id: str, username: str, db: firestore.Client = Depends(get_db)):
    """
    Gestión de conexión de tanques con verificación en Firestore.
    """
    await websocket.accept()

    # 1. MI CONTROL DE SEGURIDAD: Busco al usuario en Firestore (usando username como ID)
    user_doc = db.collection("users").document(username).get()
    
    if not user_doc.exists:
        print(f"DEBUG MÍO: Intento de entrada ilegal de '{username}'. No existe en Firebase.")
        await websocket.close(code=4003)
        return

    # 2. Si ha pasado el control, lo meto en la sala.
    await manager.connect_already_accepted(websocket, room_id)
    
    await manager.broadcast_to_room({
        "tipo": "sistema",
        "contenido": f"{username} se ha unido a la partida en {room_id} (Verificado en Firebase)"
    }, room_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            try:
                estado_validado = TankState(**data)
                
                # ¡AQUÍ GUARDO EN MI MEMORIA!
                manager.update_state(room_id, username, estado_validado.dict())
                
                paquete = {
                    "jugador": username,
                    "datos": estado_validado.dict(),
                    "tipo": "movimiento"
                }
                
                await manager.broadcast_to_room(paquete, room_id, exclude_self=websocket)

            except ValidationError as e:
                print(f"Ojo: {username} ha mandado datos inválidos: {e}")
                continue 
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, username)
        await manager.broadcast_to_room({
            "tipo": "sistema",
            "contenido": f"{username} se ha ido de la partida."
        }, room_id)
    except Exception as e:
        print(f"Me ha petado el WebSocket de {username}: {e}")
        manager.disconnect(websocket, room_id, username)
