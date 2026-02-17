from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db_sql import Base

class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) # Firebase UID o identificador de usuario
    username = Column(String, nullable=True) # Guardamos el nombre por si el usuario es borrado
    action = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
