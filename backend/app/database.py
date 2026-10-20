
from pathlib import Path

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass

DB_PATH = Path(__file__).resolve().parents[1]/"data"/"studymatch.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def activar_referencias(conexion, registro):
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def get_db():
    with SessionLocal() as db:
        try:
            yield db
        except Exception:
            db.rollback()
            raise


def inicializar_db():
    from app import modelos_db
    Base.metadata.create_all(bind=engine)

    # create_all crea tablas nuevas, pero no agrega columnas a las existentes.
    with engine.begin() as conexion:
        columnas = [columna["name"] for columna in inspect(conexion).get_columns("sesiones")]
        if "materia" not in columnas:
            conexion.execute(text(
                "ALTER TABLE sesiones ADD COLUMN materia TEXT NOT NULL DEFAULT 'General'"
            ))
