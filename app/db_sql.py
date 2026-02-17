"""
Módulo de configuración de base de datos SQL (SQLAlchemy).

Este módulo establece la conexión con la base de datos SQLite local utilizada 
para el sistema de auditoría. Define la sesión y la base para los modelos ORM.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Base de datos SQLite local para auditoría
SQLALCHEMY_DATABASE_URL = "sqlite:///./audit.db"

# check_same_thread=False es necesario solo para SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db_sql() -> Generator[Session, None, None]:
    """
    Generador de dependencia para obtener una sesión de base de datos SQL.

    Proporciona una instancia de `SessionLocal` para ser inyectada en los endpoints
    de FastAPI. Asegura que la sesión se cierre correctamente después de su uso.

    Yields:
        Session: Una sesión activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
