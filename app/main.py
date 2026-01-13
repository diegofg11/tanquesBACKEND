from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.models import user
from app.api import users
from app.api.game import manager 
from app.schemas.game import TankState # Este es el filtro que me he creado para validar los datos
from pydantic import ValidationError    # Lo necesito para capturar fallos en los datos

# --- CONFIGURACIÓN DE MI BASE DE DATOS ---
# Con esto hago que se creen las tablas automáticamente si no existen todavía.
Base.metadata.create_all(bind=engine)

# --- MI INSTANCIA PRINCIPAL ---
app = FastAPI(
    title="Tanques API",
    description="Backend para mi juego de tanques",
    version="0.1.0"
)

# Aquí conecto mis rutas de usuarios (registro y login) al servidor principal
app.include_router(users.router)

# --- MIS MANEJADORES DE ERRORES ---
# Esto lo pongo para que si falla una validación, el servidor me responda algo que yo entienda.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"message": "He detectado un error de validación", "detalle": exc.errors()},
    )

# Este es mi "salvavidas" para capturar cualquier otro error que se me haya escapado.
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Ha petado algo interno", "detalle": str(exc)},
    )

# --- MI RUTA DE BIENVENIDA ---
@app.get("/")
async def root():
    return {
        "mensaje": "¡Mi API de Tanques está en marcha!",
        "doc_url": "/docs" # Mi chuleta de documentación automática
    }

# --- MI LÓGICA DE WEBSOCKETS (CON MI FILTRO DE SEGURIDAD) ---

@app.websocket("/ws/game/{room_id}/{username}")
async def game_websocket(websocket: WebSocket, room_id: str, username: str):
    """
    Aquí es donde gestiono la conexión de los tanques.
    He metido validación con Pydantic para no volverme loco con errores de datos.
    """
    # 1. Meto al jugador en la sala que ha pedido.
    # El conserje ahora también le mandará lo que hay en memoria nada más conectar.
    await manager.connect(websocket, room_id)
    
    # 2. Lanzo un mensaje de sistema para avisar a los demás.
    await manager.broadcast_to_room({
        "tipo": "sistema",
        "contenido": f"{username} se ha unido a mi partida en {room_id}"
    }, room_id)
    
    try:
        while True:
            # 3. Me quedo esperando a que el cliente me mande un JSON.
            data = await websocket.receive_json()
            
            try:
                # 4. PASO MI FILTRO:
                estado_validado = TankState(**data)
                
                # 5. ¡AQUÍ GUARDO EN MI MEMORIA!
                # Antes de repartirlo, me apunto dónde está este tanque para los que vengan luego.
                manager.update_state(room_id, username, estado_validado.dict())
                
                # 6. Si los datos están bien, monto mi paquete para repartirlo.
                paquete = {
                    "jugador": username,
                    "datos": estado_validado.dict(),
                    "tipo": "movimiento"
                }
                
                # 7. Lo reenvío a toda la sala con total tranquilidad.
                await manager.broadcast_to_room(paquete, room_id)

            except ValidationError as e:
                # Si me mandan basura, paso del mensaje y lo imprimo en mi consola para verlo.
                print(f"Ojo: {username} me ha mandado datos que no me valen: {e.json()}")
                continue 
            
    except WebSocketDisconnect:
        # Si alguien se desconecta, lo limpio de mi gestor (con su nombre para borrar su memoria).
        manager.disconnect(websocket, room_id, username)
        await manager.broadcast_to_room({
            "tipo": "sistema",
            "contenido": f"{username} se ha ido de la partida."
        }, room_id)
    except Exception as e:
        # Error inesperado, saco al jugador por si acaso.
        print(f"Me ha petado el WebSocket de {username}: {e}")
        manager.disconnect(websocket, room_id, username)
