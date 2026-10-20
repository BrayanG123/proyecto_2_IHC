import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class TestFlujoHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        cls.url = f"http://127.0.0.1:{port}"
        # El servidor de prueba usa SQLite en memoria y no toca los datos locales.
        bootstrap = (
            "from sqlalchemy import create_engine; "
            "from sqlalchemy.pool import StaticPool; "
            "from app import database; "
            "database.engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool); "
            "database.SessionLocal.configure(bind=database.engine); "
            "import uvicorn; "
            f"uvicorn.run('main:app',host='127.0.0.1',port={port},log_level='error')"
        )
        cls.proceso = subprocess.Popen(
            [sys.executable, "-c", bootstrap],
            cwd=Path(__file__).resolve().parents[1],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        cls.addClassCleanup(cls.detener_servidor)
        for _ in range(100):
            try:
                with urlopen(cls.url + "/openapi.json", timeout=1):
                    return
            except (URLError, TimeoutError):
                if cls.proceso.poll() is not None:
                    raise RuntimeError("No se pudo iniciar el servidor de prueba.")
                time.sleep(0.1)
        raise RuntimeError("El servidor de prueba no responde.")

    @classmethod
    def detener_servidor(cls):
        cls.proceso.terminate()
        cls.proceso.wait(timeout=10)

    def request(self, path, method="GET", data=None, token=None, extra_headers=None):
        headers = {"Origin": "http://127.0.0.1:5173"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        headers.update(extra_headers or {})
        req = Request(self.url + path, method=method, headers=headers,
                      data=json.dumps(data).encode() if data is not None else None)
        try:
            response = urlopen(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            body = response.read()
            return response.status, json.loads(body) if body else None, response.headers

    def test_registro_login_creacion_y_consulta(self):
        cuenta = {"nombre": "Prueba HTTP", "email": "http@example.test", "password": "Clave123"}
        status, _, headers = self.request("/registro", "POST", cuenta)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Access-Control-Allow-Origin"], "http://127.0.0.1:5173")
        status, login, _ = self.request("/login", "POST", cuenta)
        self.assertEqual(status, 200)
        token = login["token"]
        status, perfil, _ = self.request("/perfil", token=token)
        self.assertEqual((status, perfil["email"]), (200, cuenta["email"]))
        sesion = {"nombre": "Repaso", "fecha": "2026-10-20", "modalidad": "virtual",
                  "cupo": 5, "inscripciones": False}
        status, creada, _ = self.request("/guardar-nuevo", "POST", sesion, token)
        self.assertEqual(status, 200)
        status, listado, _ = self.request("/all-sesions", token=token)
        self.assertEqual(status, 200)
        guardada = next(s for s in listado if s["id"] == creada["id"])
        self.assertIs(guardada["inscripciones_abiertas"], False)
        self.assertEqual(guardada["fecha"], sesion["fecha"])
        status, _, _ = self.request("/guardar-nuevo", "POST", {**sesion, "cupo": -1}, token)
        self.assertEqual(status, 422)

    def test_inscripcion_y_filtros_con_usuario_autenticado(self):
        from datetime import timedelta
        from app.repositorio import fecha_actual

        creador = {"nombre": "Creador", "email": "creador@example.test", "password": "Clave123"}
        estudiante = {"nombre": "Alumno", "email": "alumno@example.test", "password": "Clave123"}
        for cuenta in (creador, estudiante):
            self.assertEqual(self.request("/registro", "POST", cuenta)[0], 200)
        token_creador = self.request("/login", "POST", creador)[1]["token"]
        token_alumno = self.request("/login", "POST", estudiante)[1]["token"]
        sesion = {"nombre": "Practica HTTP", "materia": "Matematica", "cupo": 1,
                  "fecha": str(fecha_actual() + timedelta(days=1)),
                  "modalidad": "virtual", "inscripciones": True}
        status, creada, _ = self.request("/guardar-nuevo", "POST", sesion, token_creador)
        self.assertEqual(status, 200)
        ruta = f"/sesiones/{creada['id']}/inscribirse"
        self.assertEqual(self.request(ruta, "POST")[0], 401)
        self.assertEqual(self.request(ruta, "POST", token=token_creador)[0], 400)
        consulta = "/all-sesions?materia=Matematica&modalidad=virtual&disponible=true"
        status, lista, _ = self.request(consulta, token=token_alumno)
        self.assertEqual(status, 200)
        self.assertEqual([s["id"] for s in lista], [creada["id"]])
        self.assertEqual(self.request(ruta, "POST", token=token_alumno)[0], 200)
        self.assertEqual(self.request(ruta, "POST", token=token_alumno)[0], 400)
        nuevo_token = self.request("/login", "POST", estudiante)[1]["token"]
        status, lista, _ = self.request("/all-sesions?nombre=Practica", token=nuevo_token)
        self.assertEqual(status, 200)
        self.assertTrue(lista[0]["inscrito"])
        self.assertEqual(lista[0]["cupos_disponibles"], 0)
        self.assertEqual(self.request(consulta, token=token_alumno)[1], [])
        self.assertEqual(self.request("/all-sesions?periodo=rango", token=token_alumno)[0], 400)
        self.assertEqual(self.request("/all-sesions?modalidad=otra", token=token_alumno)[0], 422)
        self.assertIn("Matematica", self.request("/materias", token=token_alumno)[1])

    def test_errores_de_acceso_y_preflight_tienen_cors(self):
        status, _, headers = self.request("/login", "POST", {"email": "nadie@example.test", "password": "123"})
        self.assertEqual(status, 401)
        self.assertEqual(headers["Access-Control-Allow-Origin"], "http://127.0.0.1:5173")
        status, _, _ = self.request("/perfil", token="token-invalido")
        self.assertEqual(status, 401)
        req = Request(self.url + "/login", method="OPTIONS", headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        })
        with urlopen(req, timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://127.0.0.1:5173")
