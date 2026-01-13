from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Aquí digo dónde voy a guardar mis datos.
# He elegido SQLite para que se me cree un archivo 'sql_app.db' aquí mismo y sea fácil de manejar.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. Me creo este "engine" (motor) para que se encargue de hablar con mi archivo .db
# Le pongo check_same_thread en False porque si no SQLite se queja al usar hilos.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. La 'SessionLocal' es mi fábrica de sesiones. 
# Cada vez que quiera leer o guardar algo, le pediré una sesión a esta fábrica.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Mi 'Base' es de donde van a colgar todas mis tablas.
# Es mi molde maestro para que SQLAlchemy sepa qué tablas tiene que crear.
Base = declarative_base()

# Esta función me la he hecho para abrir y cerrar la conexión sola cada vez que la necesite.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
