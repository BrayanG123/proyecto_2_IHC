


from datetime import date

from app.database import sesiones


import unittest

from app.models import SesionDeEstudio
from app.routes import cerrar_inscripciones, crear_sesion


class TestCerrarInscripciones(unittest.TestCase):

    def setUp(self):
        self.sesiones_anteriores = sesiones.copy()
        sesiones.clear()


    def tearDown(self):
        sesiones.clear()
        sesiones.update(self.sesiones_anteriores)

    # 1. preparar
    # 2. actuar
    # 3. comprobar
    def test_cerrar_inscripciones(self):
        data = SesionDeEstudio(
            nombre="sesion fisica",
            fecha=date(2026, 10, 20),
            modalidad="prescencial",
            cupo="5",
            inscripciones=True,
        )

        crear_sesion(data)

        self.assertIs(
            sesiones["sesion fisica"]["inscripciones"],
            True,
            "antes de cerrar, la sesion debe estar abierta",
        )

        data_para_cerrar = SesionDeEstudio(
            nombre="sesion fisica",
            fecha=date(2026, 10, 20),
            modalidad="prescencial",
            cupo="5",
            inscripciones=False,
        )

        cerrar_inscripciones(data_para_cerrar)

        sesion_guardada = sesiones["sesion fisica"]

        self.assertIs(
            sesion_guardada["inscripciones"],
            False,
            "despues de cerrar, las inscripciones deben quedar cerradas",
        )
