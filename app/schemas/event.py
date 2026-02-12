from pydantic import BaseModel
from typing import Dict, Any, Optional

class EventCreate(BaseModel):
    game_token: str
    event_type: str # EJ: "ENEMY_KILLED", "DAMAGE_TAKEN", "ITEM_PICKUP", "LEVEL_START", "LEVEL_END"
    event_data: Optional[Dict[str, Any]] = {} # Datos extra: { "enemy_type": "Orc", "damage": 10 }
