from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.models import user
from app.api import users
from app.api.game import manager 
from app.schemas.game import TankState # Nuestro nuevo "Filtro" de datos
from pydantic import ValidationError    # Para capturar errores de validación

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
# Esta línea crea automáticamente las tablas en el archivo .db si no existen.
Base.metadata.create_all(bind=engine)

# --- INSTANCIA PRINCIPAL ---
app = FastAPI(
    title="Tanques API",
    description="Backend para el videojuego de tanques multi-jugador",
    version="0.1.0"
)

# Conectamos las rutas de usuarios (Registro, Login)
app.include_router(users.router)

# --- MANEJADORES DE ERRORES ---
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

# --- ENDPOINTS BÁSICOS ---
@app.get("/")
async def root():
    return {
        "mensaje": "¡Bienvenido a la API de Tanques!",
        "estado": "Funcionando correctamente",
        "doc_url": "/docs"
    }

# --- WEBSOCKETS PARA EL MULTIJUGADOR (CON VALIDACIÓN) ---

@app.websocket("/ws/game/{room_id}/{username}")
async def game_websocket(websocket: WebSocket, room_id: str, username: str):
    """
    Punto de conexión para los tanques. Ahora con validación Pydantic.
    """
    # 1. Registramos al jugador en la sala.
    await manager.connect(websocket, room_id)
    
    # 2. Mensaje inicial de sistema.
    await manager.broadcast_to_room({
        "tipo": "sistema",
        "contenido": f"{username} ha entrado a la sala {room_id}"
    }, room_id)
    
    try:
        while True:
            # 3. Recibimos el JSON "crudo" del cliente.
            data = await websocket.receive_json()
            
            try:
                # 4. PASAMOS EL FILTRO (Pydantic):
                # Intentamos convertir el JSON en un objeto TankState.
                # Si falta la vida, o la rotación es 500, esto lanzará un ValidationError.
                estado_validado = TankState(**data)
                
                # 5. Si los datos son válidos, preparamos el paquete.
                # .dict() convierte el objeto TankState de vuelta a un diccionario de Python.
                paquete = {
                    "jugador": username,
                    "datos": estado_validado.dict(),
                    "tipo": "movimiento"
                }
                
                # 6. Reenviamos con total seguridad a la sala.
                await manager.broadcast_to_room(paquete, room_id)

            except ValidationError as e:
                # Si los datos están mal, el servidor no se cae.
                # Simplemente ignoramos este paquete corrupto y avisamos por consola.
                print(f"AVISO: {username} envió datos inválidos: {e.json()}")
                continue 
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast_to_room({
            "tipo": "sistema",
            "contenido": f"{username} ha salido de la partida."
        }, room_id)
    except Exception as e:
        print(f"Error inesperado en WebSocket ({username}): {e}")
        manager.disconnect(websocket, room_id)

# --------------------------------------
