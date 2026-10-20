from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modelos_db import SesionEstudio
from app.models import CambiarPassword, Login, RecuperarPassword, Registro
from app.repositorio import get_user_by_email
from app.routes import (
    cambiar_password, crear_sesion, iniciar_sesion, perfil,
    recuperar_password, registrar_usuario,
)
from app.services import obtener_usuario_actual, verificar_password
from tests.base_db import PruebaConBaseDeDatos


class TestAcceso(PruebaConBaseDeDatos):
    def registrar(self):
        registrar_usuario(Registro(nombre="Demo", email=" Demo@example.test ", password="Clave123"), self.db)

    def test_registro_login_y_perfil_persistidos(self):
        self.registrar()
        with Session(self.engine) as db:
            usuario = get_user_by_email(db, "demo@example.test")
            self.assertNotEqual(usuario.password_hash, "Clave123")
            self.assertTrue(verificar_password("Clave123", usuario.password_hash))
            resultado = iniciar_sesion(Login(email="DEMO@example.test", password="Clave123"), db)
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=resultado["token"])
            actual = obtener_usuario_actual(credentials, db)
            self.assertEqual(perfil(actual), {"nombre": "Demo", "email": "demo@example.test"})

    def test_rechaza_duplicado_y_password_incorrecto(self):
        self.registrar()
        with self.assertRaises(HTTPException) as duplicado:
            self.registrar()
        self.assertEqual(duplicado.exception.status_code, 409)
        with self.assertRaises(HTTPException) as acceso:
            iniciar_sesion(Login(email="demo@example.test", password="incorrecta"), self.db)
        self.assertEqual(acceso.exception.status_code, 401)

    def test_recuperacion_invalida_el_codigo_usado(self):
        self.registrar()
        codigo = recuperar_password(RecuperarPassword(email="demo@example.test"), self.db)["codigo"]
        datos = CambiarPassword(email="demo@example.test", codigo=codigo, nueva_password="Nueva123")
        cambiar_password(datos, self.db)
        iniciar_sesion(Login(email="demo@example.test", password="Nueva123"), self.db)
        with self.assertRaises(HTTPException):
            cambiar_password(datos, self.db)

    def test_rechaza_cupos_invalidos(self):
        for cupo in (0, -1, 1.5):
            with self.subTest(cupo=cupo), self.assertRaises(ValidationError):
                self.datos_sesion().model_validate({**self.datos_sesion().model_dump(), "cupo": cupo})

    def test_impide_cerrar_sesion_ajena(self):
        from app.routes import cerrar_inscripciones

        resultado = crear_sesion(self.datos_sesion(), self.db, self.usuario)
        self.registrar()
        otro = get_user_by_email(self.db, "demo@example.test")
        with self.assertRaises(HTTPException):
            cerrar_inscripciones(self.datos_sesion(False), self.db, otro)
        self.assertTrue(self.db.get(SesionEstudio, resultado["id"]).inscripciones_abiertas)

    def test_exige_usuario_existente_en_sesion(self):
        sesion = SesionEstudio(nombre="Prueba", fecha=self.datos_sesion().fecha,
                              modalidad="virtual", cupo=5, usuario_id=999)
        self.db.add(sesion)
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()
