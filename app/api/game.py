from fastapi import WebSocket
import json
from typing import List, Dict

# El ConnectionManager es como el "Conserje" de un hotel.
# Ahora, en lugar de una sola sala de espera, tiene varias habitaciones (Rooms).
class ConnectionManager:
    def __init__(self):
        # Usamos un diccionario: { "nombre_sala": [lista_de_websockets] }
        # Esto nos permite separar a los jugadores en diferentes partidas.
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        """Acepta la conexión y mete al jugador en una sala específica."""
        await websocket.accept()
        
        # Si la sala no existe todavía, la creamos vacía
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
            
        # Añadimos el websocket del jugador a su sala
        self.active_rooms[room_id].append(websocket)
        print(f"Tanque unido a sala '{room_id}'. Jugadores en sala: {len(self.active_rooms[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        """Saca al jugador de la sala cuando se desconecta."""
        if room_id in self.active_rooms:
            self.active_rooms[room_id].remove(websocket)
            # Si la sala se queda vacía, la eliminamos para ahorrar memoria
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
        print(f"Tanque salió de sala '{room_id}'.")

    async def broadcast_to_room(self, message: dict, room_id: str):
        """
        Envía un mensaje JSON a todos los jugadores de UNA SOLA sala.
        El mensaje ahora es un diccionario de Python que convertiremos a JSON.
        """
        if room_id in self.active_rooms:
            # Recorremos solo los jugadores de esa sala
            for connection in self.active_rooms[room_id]:
                try:
                    # send_json es una función de FastAPI que convierte el dict a texto automáticamente
                    await connection.send_json(message)
                except Exception:
                    # Si falla (ej: el jugador cerró el navegador de golpe), lo ignoramos
                    pass

# Creamos la instancia única que gestionará todo el tinglado
manager = ConnectionManager()
