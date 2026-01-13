import asyncio
import websockets
import json

async def test_connect():
    uri = "ws://localhost:8000/ws/game/SALA_TEST/USER_TEST"
    try:
        async with websockets.connect(uri) as websocket:
            print("Conexión exitosa al servidor!")
            # Recibir mensaje de bienvenida
            msg = await websocket.recv()
            print(f"Recibido: {msg}")
            
            # Enviar un movimiento
            await websocket.send(json.dumps({"x": 10, "y": 20}))
            print("Mensaje de prueba enviado.")
            
            # Recibir eco del movimiento
            msg = await websocket.recv()
            print(f"Recibido (eco): {msg}")
    except Exception as e:
        print(f"Error conectando: {e}")

if __name__ == "__main__":
    asyncio.run(test_connect())
