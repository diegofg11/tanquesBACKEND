from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware # Mi llave para dejar entrar peticiones web
from fastapi.exceptions import RequestValidationError
# ... resto de imports ...

# --- MI INSTANCIA PRINCIPAL ---
app = FastAPI(
    title="Tanques API",
    description="Backend para mi juego de tanques",
    version="0.1.0"
)

# ME DOY PERMISOS DE CORS:
# Esto es vital para que mi simulador HTML pueda registrar usuarios mediante peticiones HTTP.
# Si no lo pongo, el navegador bloqueará mis intentos de registro por seguridad.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Por ahora dejo entrar a cualquiera, luego lo cerraré.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# --- MI LÓGICA DE WEBSOCKETS (CON VERIFICACIÓN DE USUARIO) ---

@app.websocket("/ws/game/{room_id}/{username}")
async def game_websocket(websocket: WebSocket, room_id: str, username: str, db: Session = Depends(get_db)):
    """
    Aquí es donde gestiono la conexión de los tanques.
    Ahora solo dejo pasar a los que estén registrados en mi base de datos.
    """
    # 1. Antes de nada, acepto la conexión técnica para poder hablar.
    await websocket.accept()

    # 2. MI CONTROL DE SEGURIDAD: Busco al usuario en mi base de datos SQL.
    user_db = db.query(User).filter(User.username == username).first()
    
    if not user_db:
        # Si no lo encuentro, le mando un mensaje y chapo la conexión.
        # Uso el código 4003 que significa "Violación de política".
        print(f"DEBUG MÍO: Intento de entrada ilegal de '{username}'.")
        await websocket.close(code=4003)
        return

    # 3. Si ha pasado el control, lo meto en la sala.
    # El conserje ahora también le mandará lo que hay en memoria nada más conectar.
    await manager.connect_already_accepted(websocket, room_id)
    
    # 4. Lanzo un mensaje de sistema para avisar a los demás.
    await manager.broadcast_to_room({
        "tipo": "sistema",
        "contenido": f"{username} se ha unido a mi partida en {room_id}"
    }, room_id)
    
    try:
        while True:
            # 5. Me quedo esperando a que el cliente me mande un JSON.
            data = await websocket.receive_json()
            
            try:
                # 6. PASO MI FILTRO:
                estado_validado = TankState(**data)
                
                # 7. ¡AQUÍ GUARDO EN MI MEMORIA!
                manager.update_state(room_id, username, estado_validado.dict())
                
                # 8. Si los datos están bien, monto mi paquete para repartirlo.
                paquete = {
                    "jugador": username,
                    "datos": estado_validado.dict(),
                    "tipo": "movimiento"
                }
                
                # 9. Lo reenvío a toda la sala con total tranquilidad.
                await manager.broadcast_to_room(paquete, room_id, exclude_self=websocket)

            except ValidationError as e:
                print(f"Ojo: {username} me ha mandado datos que no me valen: {e.json()}")
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
