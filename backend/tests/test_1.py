


from datetime import date

from app.database import sesiones

import unittest

from app.models import SesionDeEstudio
from app.routes import crear_sesion


class PruebaDeEstadoInicial(unittest.TestCase):
    def setUp(self):
        self.sesiones_anteriores = sesiones.copy()
        sesiones.clear()

    def tearDown(self):
        sesiones.clear()
        sesiones.update(self.sesiones_anteriores)

    def test_estado_inicial_true(self):

        data = SesionDeEstudio(
            nombre="sesion fisica",
            fecha=date(2026, 10, 20),
            modalidad="prescencial",
            cupo="5",
            inscripciones=True
        )

        crear_sesion(data)

        sesion_guardada = sesiones["sesion fisica"]

        self.assertIs(
            sesion_guardada["inscripciones"],
            True,
            "la sesion nueva debe qedar con la inscripciones abiertas",
        )