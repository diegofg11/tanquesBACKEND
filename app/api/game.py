from fastapi import WebSocket
import json
from typing import List, Dict

# El ConnectionManager es como el "Conserje" de un hotel.
# Ahora, en lugar de una sola sala de espera, tiene varias habitaciones (Rooms).
class ConnectionManager:
    def __init__(self):
        # Usamos un diccionario (como una agenda): { "nombre_sala": [lista_de_websockets] }
        # La clave es el ID de la sala y el valor es la lista de jugadores que están dentro.
        # Esto permite que los jugadores de la "PARTIDA_A" no reciban mensajes de la "PARTIDA_B".
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        """Acepta la conexión técnica y mete al jugador en su habitación."""
        await websocket.accept()
        
        # Si somos el primero en pedir esta sala, el conserje crea la lista vacía.
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
            
        # Metemos el cable (websocket) del jugador en la lista de su sala.
        self.active_rooms[room_id].append(websocket)
        print(f"DEBUG: Tanque unido a '{room_id}'. Total en sala: {len(self.active_rooms[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        """Limpia el registro cuando un jugador se va."""
        if room_id in self.active_rooms:
            # Sacamos el cable de la lista de esa sala.
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
            
            # ¡Importante!: Si la sala se queda vacía, la borramos del diccionario.
            # Esto evita que el servidor gaste memoria guardando salas que ya nadie usa.
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
        print(f"DEBUG: Tanque salió de '{room_id}'.")

    async def broadcast_to_room(self, message: dict, room_id: str):
        """
        Envía un paquete de datos a TODOS los jugadores de una sala específica.
        'message' es un diccionario de Python que FastAPI transformará en JSON automáticamente.
        """
        if room_id in self.active_rooms:
            # Buscamos la lista de la sala y recorremos cable por cable.
            for connection in self.active_rooms[room_id]:
                try:
                    # send_json() hace el trabajo sucio de convertir el dict a texto y enviarlo.
                    await connection.send_json(message)
                except Exception:
                    # Si un envío falla (ej: cable roto), no bloqueamos a los demás jugadores.
                    pass

# Creamos una ÚNICA instancia (Singleton) para que todo el servidor use el mismo conserje.
manager = ConnectionManager()
