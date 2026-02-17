from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditBase(BaseModel):
    user_id: str
    username: Optional[str] = None
    action: str

class AuditCreate(AuditBase):
    pass

class Audit(AuditBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
