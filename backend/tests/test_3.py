from fastapi import HTTPException
from app.modelos_db import SesionEstudio
from app.routes import cerrar_inscripciones, crear_sesion
from tests.base_db import PruebaConBaseDeDatos


class TestCerrarDeNuevo(PruebaConBaseDeDatos):
    def test_rechazar_sesion_ya_cerrada(self):
        resultado = crear_sesion(self.datos_sesion(), self.db, self.usuario)
        cerrar_inscripciones(self.datos_sesion(False), self.db, self.usuario)
        with self.assertRaises(HTTPException) as rechazo:
            cerrar_inscripciones(self.datos_sesion(False), self.db, self.usuario)
        self.assertEqual(rechazo.exception.status_code, 400)
        self.db.refresh(self.db.get(SesionEstudio, resultado["id"]))
        self.assertIs(self.db.get(SesionEstudio, resultado["id"]).inscripciones_abiertas, False)
