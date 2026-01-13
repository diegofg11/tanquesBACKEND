from fastapi import WebSocket
import json
from typing import List, Dict

# Mi ConnectionManager es como mi "Conserje" privado.
# He decidido que tenga varias "habitaciones" (Rooms) para separar los juegos.
class ConnectionManager:
    def __init__(self):
        # Me creo un diccionario para organizar las salas: { "nombre_sala": [lista_de_jugadores] }
        self.active_rooms: Dict[str, List[WebSocket]] = {}
        
        # AQUÍ ESTÁ MI MEJORA: Un diccionario para guardar el estado de cada tanque.
        # Estructura: { "id_sala": { "nombre_usuario": { "x": 0, "y": 0, ... } } }
        self.room_states: Dict[str, Dict[str, dict]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        """Acepto la conexión y meto al tío en su habitación."""
        await websocket.accept()
        
        # Si soy el primero en entrar a esta sala, la tengo que crear yo.
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = []
            self.room_states[room_id] = {} # También inicializo la memoria de la sala
            
        # Añado el cable (websocket) de este jugador a su lista.
        self.active_rooms[room_id].append(websocket)
        
        # AHORA: Le mando al nuevo jugador todo lo que tengo en mi memoria de esta sala.
        # Así verá a los demás tanques nada más entrar.
        for existing_user, state in self.room_states[room_id].items():
            await websocket.send_json({
                "jugador": existing_user,
                "datos": state,
                "tipo": "movimiento"
            })
            
        print(f"DEBUG MÍO: He unido a alguien a '{room_id}'. Ya somos {len(self.active_rooms[room_id])}")

    def update_state(self, room_id: str, username: str, state: dict):
        """Guardo en mi memoria lo último que me ha dicho este tanque."""
        if room_id in self.room_states:
            self.room_states[room_id][username] = state

    def disconnect(self, websocket: WebSocket, room_id: str, username: str = None):
        """Limpio el rastro cuando alguien se desconecta."""
        if room_id in self.active_rooms:
            if websocket in self.active_rooms[room_id]:
                self.active_rooms[room_id].remove(websocket)
            
            # Si me han pasado el nombre, también lo borro de mi memoria de posiciones.
            if username and username in self.room_states.get(room_id, {}):
                del self.room_states[room_id][username]
                
            # Si veo que la sala se ha quedado vacía, borro todo lo relacionado.
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
                if room_id in self.room_states:
                    del self.room_states[room_id]
                    
        print(f"DEBUG MÍO: {username} se ha pirado de '{room_id}'.")

    async def broadcast_to_room(self, message: dict, room_id: str):
        """Envío el paquete a TODOS los que estén en esta sala."""
        if room_id in self.active_rooms:
            for connection in self.active_rooms[room_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

# Me creo una única instancia para que todo mi servidor use el mismo gestor.
manager = ConnectionManager()
