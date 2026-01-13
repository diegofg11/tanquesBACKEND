from fastapi import WebSocket
import json
from typing import List, Dict

# Mi ConnectionManager es como mi "Conserje" privado.
# He decidido que tenga varias "habitaciones" (Rooms) para separar los juegos.
class ConnectionManager:
    def __init__(self):
        # Me creo un diccionario para organizar las salas: { "nombre_sala": [lista_de_jugadores] }
        # Así evito que los mensajes de una partida se mezclen con los de otra.
        self.active_rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        """Acepto la conexión y meto al tío en su habitación."""
        await websocket.accept()
        
        # Si soy el primero en entrar a esta sala, la tengo que crear yo.
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
            
        # Añado el cable (websocket) de este jugador a su lista.
        self.active_rooms[room_id].append(websocket)
        print(f"DEBUG MÍO: He unido a alguien a '{room_id}'. Ya somos {len(self.active_rooms[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        """Limpio el rastro cuando alguien se desconecta."""
        if room_id in self.active_rooms:
            # Saco el cable de la lista de esa sala.
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
            
            # Si veo que la sala se ha quedado vacía, la borro para que no me chupe RAM.
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
        print(f"DEBUG MÍO: Alguien se ha pirado de '{room_id}'.")

    async def broadcast_to_room(self, message: dict, room_id: str):
        """
        Envío el paquete a TODOS los que estén en esta sala.
        El mensaje me llega como un diccionario y FastAPI me lo pasa a JSON solo.
        """
        if room_id in self.active_rooms:
            # Recorro uno a uno todos los cables de esta habitación.
            for connection in self.active_rooms[room_id]:
                try:
                    # Uso send_json para no tener que andar convirtiendo yo el texto.
                    await connection.send_json(message)
                except Exception:
                    # Si falla el envío a uno (ej: ha cerrado el PC), no quiero que se me pare el resto.
                    pass

# Me creo una única instancia para que todo mi servidor use el mismo gestor.
manager = ConnectionManager()
