from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definimos dónde estará nuestro archivo de base de datos.
# "sqlite:///./sql_app.db" le dice a SQLAlchemy que use SQLite y cree un archivo llamado 'sql_app.db' en esta carpeta.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. El 'engine' (motor) es el que se encarga de hablar directamente con el archivo .db
# 'check_same_thread': False es necesario solo para SQLite en entornos multihilo.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. La 'SessionLocal' es una fábrica de conexiones. 
# Cada vez que queramos leer o escribir algo, pediremos una sesión a esta fábrica.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 'Base' es la clase de la que heredarán todos nuestros modelos (tablas).
# Es como el molde maestro para crear tablas en la base de datos.
Base = declarative_base()

# Esta función nos ayuda a abrir y cerrar la conexión automáticamente cada vez que la usamos.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
