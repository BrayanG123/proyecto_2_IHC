import unittest
from datetime import date

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.database import Base
from app.models import SesionDeEstudio
from app.repositorio import guardar_usuario


class PruebaConBaseDeDatos(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")

        @event.listens_for(self.engine, "connect")
        def activar_referencias(conexion, registro):
            conexion.execute("PRAGMA foreign_keys=ON")

        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine, expire_on_commit=False)
        self.usuario = guardar_usuario(self.db, "Estudiante", "estudiante@example.test", "hash")

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def datos_sesion(self, abiertas=True):
        return SesionDeEstudio(
            nombre="Repaso de fisica", fecha=date(2026, 10, 20),
            modalidad="presencial", cupo=5, inscripciones=abiertas,
        )
