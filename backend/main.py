
from datetime import datetime, timedelta, timezone
from pathlib import Path
import secrets
import sys

import bcrypt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel


# ============================================================
# CONFIGURACIÓN
# ============================================================

app = FastAPI(
    title="StudyMatch API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = "studymatch-clave-secreta-para-desarrollo"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


# ============================================================
# UBICACIÓN DEL FRONTEND
# ============================================================

# Cuando ejecutamos normalmente:
#
# proyecto_2_IHC/
# ├── backend/
# │   └── main.py
# └── frontend/
#     └── dist/
#
# Cuando está convertido a .exe, PyInstaller coloca los
# archivos adicionales dentro de una carpeta temporal.

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent


FRONTEND_DIR = BASE_DIR / "frontend" / "dist"
INDEX_FILE = FRONTEND_DIR / "index.html"
ASSETS_DIR = FRONTEND_DIR / "assets"


# ============================================================
# BASE DE DATOS TEMPORAL
# ============================================================

# Los usuarios se pierden cuando se reinicia FastAPI.
usuarios = {}


security = HTTPBearer(auto_error=False)


# ============================================================
# MODELOS
# ============================================================

class Registro(BaseModel):
    nombre: str
    email: str
    password: str


class Login(BaseModel):
    email: str
    password: str


class RecuperarPassword(BaseModel):
    email: str


class CambiarPassword(BaseModel):
    email: str
    codigo: str
    nueva_password: str


# ============================================================
# FUNCIONES DE CONTRASEÑA
# ============================================================

def normalizar_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# ============================================================
# JWT
# ============================================================

def crear_token(email: str) -> str:
    ahora = datetime.now(timezone.utc)
    expiracion = ahora + timedelta(hours=TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": email,
        "iat": ahora,
        "exp": expiracion,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def obtener_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión.",
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if not email or email not in usuarios:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión no válida.",
            )

        return usuarios[email]

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
        )


# ============================================================
# API
# ============================================================

@app.post("/registro")
def registrar_usuario(datos: Registro):

    email = normalizar_email(datos.email)

    if not datos.nombre.strip():
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio."
        )

    if not email or "@" not in email:
        raise HTTPException(
            status_code=400,
            detail="Ingresa un correo válido."
        )

    if not datos.password:
        raise HTTPException(
            status_code=400,
            detail="La contraseña es obligatoria."
        )

    if email in usuarios:
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado."
        )

    usuarios[email] = {
        "nombre": datos.nombre.strip(),
        "email": email,
        "password_hash": hash_password(datos.password),
        "reset_code": None,
    }

    return {
        "mensaje": "Cuenta creada correctamente."
    }


@app.post("/login")
def iniciar_sesion(datos: Login):

    email = normalizar_email(datos.email)

    usuario = usuarios.get(email)

    if not usuario or not verificar_password(
        datos.password,
        usuario["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    token = crear_token(email)

    return {
        "mensaje": "Inicio de sesión correcto.",
        "token": token,
        "usuario": {
            "nombre": usuario["nombre"],
            "email": usuario["email"],
        },
    }


@app.get("/perfil")
def perfil(
    usuario=Depends(obtener_usuario_actual)
):
    return {
        "nombre": usuario["nombre"],
        "email": usuario["email"],
    }


@app.post("/logout")
def cerrar_sesion(
    usuario=Depends(obtener_usuario_actual)
):
    # JWT es stateless.
    # El frontend elimina el token del navegador.

    return {
        "mensaje": "Sesión cerrada correctamente."
    }


# ============================================================
# RECUPERACIÓN DE CONTRASEÑA
# ============================================================

@app.post("/recuperar-password")
def recuperar_password(datos: RecuperarPassword):

    email = normalizar_email(datos.email)

    usuario = usuarios.get(email)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="No existe una cuenta con ese correo."
        )

    # Simula el código que normalmente llegaría por correo.
    codigo = str(
        secrets.randbelow(900000) + 100000
    )

    usuario["reset_code"] = codigo

    return {
        "mensaje": "Código de recuperación generado.",
        "codigo": codigo,
        "nota": "En un sistema real, este código se enviaría por correo.",
    }


@app.post("/cambiar-password")
def cambiar_password(datos: CambiarPassword):

    email = normalizar_email(datos.email)

    usuario = usuarios.get(email)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="No existe esa cuenta."
        )

    if (
        not usuario["reset_code"]
        or datos.codigo.strip() != usuario["reset_code"]
    ):
        raise HTTPException(
            status_code=400,
            detail="El código de recuperación no es válido."
        )

    if not datos.nueva_password:
        raise HTTPException(
            status_code=400,
            detail="La nueva contraseña es obligatoria."
        )

    usuario["password_hash"] = hash_password(
        datos.nueva_password
    )

    usuario["reset_code"] = None

    return {
        "mensaje": "Contraseña cambiada correctamente."
    }


# ============================================================
# FRONTEND REACT
# ============================================================

@app.get("/")
def servir_inicio():
    """
    Sirve el index.html de React.
    """

    if not INDEX_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "No se encontró el frontend compilado. "
                "Ejecuta 'npm run build' en frontend."
            )
        )

    return FileResponse(INDEX_FILE)


@app.get("/{full_path:path}")
def servir_react(full_path: str):
    """
    Permite que React Router funcione.

    Por ejemplo:

    /login
    /register
    /recover
    /dashboard

    Todas estas rutas terminan cargando index.html.
    """

    # Primero comprobamos si existe un archivo físico.
    archivo = FRONTEND_DIR / full_path

    if archivo.is_file():
        return FileResponse(archivo)

    # Si no existe, devolvemos React.
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)

    raise HTTPException(
        status_code=404,
        detail="Frontend no encontrado."
    )
if __name__ == "__main__":
    import uvicorn
    import threading
    import webbrowser
    import time

    def abrir_navegador():
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:8000")

    threading.Thread(
        target=abrir_navegador,
        daemon=True
    ).start()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )