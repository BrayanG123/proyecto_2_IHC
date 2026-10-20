from sqlalchemy.orm import Session
from app.modelos_db import SesionEstudio
from app.routes import cerrar_inscripciones, crear_sesion
from tests.base_db import PruebaConBaseDeDatos


class TestCerrarInscripciones(PruebaConBaseDeDatos):
    def test_cerrar_inscripciones(self):
        resultado = crear_sesion(self.datos_sesion(), self.db, self.usuario)
        cerrar_inscripciones(self.datos_sesion(False), self.db, self.usuario)
        with Session(self.engine) as db:
            sesion = db.get(SesionEstudio, resultado["id"])
            self.assertIs(sesion.inscripciones_abiertas, False)
            self.assertEqual(sesion.nombre, "Repaso de fisica")
            self.assertEqual(sesion.cupo, 5)
