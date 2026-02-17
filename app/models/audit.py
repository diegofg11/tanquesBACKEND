"""
Definición del modelo ORM para la Auditoría.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db_sql import Base

class Audit(Base):
    """
    Modelo que representa una entrada en el registro de auditoría.

    Attributes:
        id (int): Identificador único del registro.
        user_id (str): ID del usuario que realizó la acción.
        username (str): Nombre de usuario en el momento de la acción.
        action (str): Descripción de la acción realizada.
        timestamp (datetime): Fecha y hora de la acción.
    """
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) 
    username = Column(String, nullable=True) 
    action = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
