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
# {room_id} y {username} son variables que FastAPI saca de la URL automáticamente.
@app.websocket("/ws/game/{room_id}/{username}")
async def game_websocket(websocket: WebSocket, room_id: str, username: str):
    """
    Punto de conexión mejorado con salas y JSON.
    Esta función se ejecuta cuando un tanque (ya sea HTML o Unity) se conecta.
    """
    # 1. Registramos al jugador en la sala que ha pedido.
    await manager.connect(websocket, room_id)
    
    # 2. Enviamos un primer mensaje de bienvenida tipo JSON.
    # Es importante que sea JSON para que el cliente (Unity/Web) siempre reciba el mismo formato.
    await manager.broadcast_to_room({
        "tipo": "sistema",
        "contenido": f"{username} ha entrado a la sala {room_id}"
    }, room_id)
    
    try:
        while True:
            # 3. Nos quedamos "escuchando" hasta que el tanque mande algo (movimiento, disparo...).
            # receive_json() es genial porque valida que lo que llegue sea un JSON válido.
            data = await websocket.receive_json()
            
            # 4. Preparamos el "paquete certificado". 
            # Le ponemos el nombre del jugador para que los demás sepan de quién es el mensaje.
            paquete = {
                "jugador": username,
                "datos": data, # Aquí dentro van x, y, rotacion, vida... lo que el cliente decidió mandar.
                "tipo": "movimiento"
            }
            
            # 5. La "Magia": Reenviamos este paquete a TODOS los de la sala (menos al que lo envió, 
            # aunque en esta versión simple se lo mandamos a todos para confirmar).
            await manager.broadcast_to_room(paquete, room_id)
            
    except WebSocketDisconnect:
        # Se ejecuta si el jugador cierra la pestaña o pierde la conexión.
        manager.disconnect(websocket, room_id)
        await manager.broadcast_to_room({
            "tipo": "sistema",
            "contenido": f"{username} ha salido de la partida."
        }, room_id)
    except Exception as e:
        # Si ocurre un error inesperado (como mandar un JSON mal formado).
        print(f"Error en WebSocket para {username}: {e}")
        manager.disconnect(websocket, room_id)

# --------------------------------------
