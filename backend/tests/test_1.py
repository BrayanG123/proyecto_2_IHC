from sqlalchemy.orm import Session
from app.modelos_db import SesionEstudio
from app.routes import crear_sesion
from tests.base_db import PruebaConBaseDeDatos


class PruebaDeEstadoInicial(PruebaConBaseDeDatos):
    def test_estado_inicial_true(self):
        resultado = crear_sesion(self.datos_sesion(), self.db, self.usuario)
        with Session(self.engine) as db:
            sesion = db.get(SesionEstudio, resultado["id"])
            self.assertIs(sesion.inscripciones_abiertas, True)
            self.assertEqual(sesion.cupo, 5)

    def test_permite_crear_inscripciones_cerradas(self):
        resultado = crear_sesion(self.datos_sesion(False), self.db, self.usuario)
        with Session(self.engine) as db:
            self.assertIs(db.get(SesionEstudio, resultado["id"]).inscripciones_abiertas, False)
