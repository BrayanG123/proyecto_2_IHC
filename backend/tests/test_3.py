


from datetime import date

from fastapi import HTTPException

from app.database import sesiones


import unittest

from app.models import SesionDeEstudio
from app.routes import cerrar_inscripciones, crear_sesion


class testCerrarDeNuevo(unittest.TestCase):

    def setUp(self):
        self.sesiones_anteriores = sesiones.copy()
        sesiones.clear()

    def tearDown(self):
        sesiones.clear()
        sesiones.update(self.sesiones_anteriores)

    def test_rechazar_sesion_ya_cerrada(self):

        data_inicial = SesionDeEstudio(
            nombre="sesion fisica",
            fecha=date(2026, 10, 20),
            modalidad="presencial",
            cupo="5",
            inscripciones=True,
        )

        crear_sesion(data_inicial)

        data_para_cerrar = SesionDeEstudio(
            nombre="sesion fisica",
            fecha=date(2026, 10, 20),
            modalidad="presencial",
            cupo="5",
            inscripciones=False,
        )

        cerrar_inscripciones(data_para_cerrar)

        self.assertIs(
            sesiones["sesion fisica"]["inscripciones"],
            False,
            "antes del segundo intento la sesion debe estar cerrada"
        )

        with self.assertRaises( HTTPException, msg="cerrar una sesion ya cerrada puede producir un rechazo"
        ):
            cerrar_inscripciones(data_para_cerrar)


        self.assertIs(
            sesiones["sesion fisica"]["inscripciones"],
            False,
            "un intento rechazado no debe reabrir la sesion",
        )