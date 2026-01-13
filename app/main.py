from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.models import user
from app.api import users
from app.api.game import manager # Importamos nuestro gestor de conexiones

# Esta línea crea automáticamente las tablas en el archivo .db si no existen.
# Es muy útil en desarrollo porque no tienes que escribir el SQL de "CREATE TABLE".
Base.metadata.create_all(bind=engine)

# Creamos la instancia principal de la aplicación.
# Este objeto 'app' es el que gestionará todas las rutas y peticiones.
app = FastAPI(
    title="Tanques API",
    description="Backend para el videojuego de tanques multi-jugador",
    version="0.1.0"
)

# Conectamos las rutas de usuarios con la aplicación principal.
app.include_router(users.router)

# --- Manejadores de errores ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "Error de validación", "detalle": exc.errors()},
    )

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Error interno", "detalle": str(exc), "tipo": str(type(exc))},
    )
# -----------------------------

# Esta es una ruta de ejemplo (Endpoint).
# @app.get("/") le dice a FastAPI que cuando alguien entre en la raíz de la web, ejecute esta función.
@app.get("/")
async def root():
    """
    Ruta de bienvenida para verificar que el servidor funciona.
    """
    return {
        "mensaje": "¡Bienvenido a la API de Tanques!",
        "estado": "Funcionando correctamente",
        "doc_url": "/docs"  # FastAPI autogenera documentación en esta ruta.
    }

# --- WEBSOCKETS PARA EL MULTIJUGADOR ---

# Nueva ruta: ws://localhost:8000/ws/game/SALA_1/diego
@app.websocket("/ws/game/{room_id}/{username}")
async def game_websocket(websocket: WebSocket, room_id: str, username: str):
    """
    Punto de conexión mejorado con salas y JSON.
    1. Se une a una sala específica (room_id).
    2. Recibe mensajes JSON (ej: {"x": 100, "y": 200}).
    3. Reenvía el JSON a todos en esa misma sala.
    """
    await manager.connect(websocket, room_id)
    
    # Mensaje inicial de sistema en formato JSON para que el cliente no explote
    # esperando datos estructurados.
    await manager.broadcast_to_room({
        "tipo": "sistema",
        "contenido": f"{username} ha entrado a la sala {room_id}"
    }, room_id)
    
    try:
        while True:
            # Ahora esperamos recibir un JSON directamente
            # Si el cliente envía algo que no es JSON, FastAPI lanzará un error aquí.
            data = await websocket.receive_json()
            
            # Preparamos el paquete de datos para reenviar
            # Le añadimos quién lo envió para que los demás sepan qué tanque se mueve
            paquete = {
                "jugador": username,
                "datos": data, # Aquí dentro irán la X, Y, rotación, etc.
                "tipo": "movimiento"
            }
            
            # Reenviamos SOLO a los de su sala
            await manager.broadcast_to_room(paquete, room_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast_to_room({
            "tipo": "sistema",
            "contenido": f"{username} ha salido de la partida."
        }, room_id)
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        manager.disconnect(websocket, room_id)

# --------------------------------------

# Nota para el futuro: Aquí es donde conectaremos las rutas de usuarios y los WebSockets.
