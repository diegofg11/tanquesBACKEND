"""
Esquemas Pydantic para el sistema de Auditoría.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditBase(BaseModel):
    """
    Esquema base para los datos comunes de auditoría.
    """
    user_id: str
    username: Optional[str] = None
    action: str

class AuditCreate(AuditBase):
    """
    Esquema para la creación de un nuevo registro de auditoría.
    """
    pass

class Audit(AuditBase):
    """
    Esquema de respuesta completa para un registro de auditoría.
    Incluye ID y timestamp generados por la base de datos.
    """
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
