from datetime import datetime, timedelta, timezone
import secrets

import bcrypt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

app = FastAPI(title="StudyMatch API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "studymatch-clave-secreta-para-desarrollo"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# Base de datos temporal para el proyecto académico.
# Los usuarios se pierden cuando se reinicia FastAPI.
usuarios = {}

security = HTTPBearer(auto_error=False)


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


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"), password_hash.encode("utf-8")
    )


def crear_token(email: str) -> str:
    ahora = datetime.now(timezone.utc)
    expiracion = ahora + timedelta(hours=TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": email,
        "iat": ahora,
        "exp": expiracion,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


@app.get("/")
def inicio():
    return {
        "mensaje": "API de StudyMatch funcionando correctamente",
        "estado": "ok",
    }


@app.post("/registro")
def registrar_usuario(datos: Registro):
    email = normalizar_email(datos.email)

    if not datos.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre es obligatorio.")

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Ingresa un correo válido.")

    if not datos.password:
        raise HTTPException(status_code=400, detail="La contraseña es obligatoria.")

    if email in usuarios:
        raise HTTPException(status_code=409, detail="El correo ya está registrado.")

    usuarios[email] = {
        "nombre": datos.nombre.strip(),
        "email": email,
        "password_hash": hash_password(datos.password),
        "reset_code": None,
    }

    return {"mensaje": "Cuenta creada correctamente."}


@app.post("/login")
def iniciar_sesion(datos: Login):
    email = normalizar_email(datos.email)
    usuario = usuarios.get(email)

    if not usuario or not verificar_password(datos.password, usuario["password_hash"]):
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
def perfil(usuario=Depends(obtener_usuario_actual)):
    return {
        "nombre": usuario["nombre"],
        "email": usuario["email"],
    }


@app.post("/logout")
def cerrar_sesion(usuario=Depends(obtener_usuario_actual)):
    # JWT es stateless. El frontend elimina el token del navegador.
    return {"mensaje": "Sesión cerrada correctamente."}


@app.post("/recuperar-password")
def recuperar_password(datos: RecuperarPassword):
    email = normalizar_email(datos.email)
    usuario = usuarios.get(email)

    if not usuario:
        raise HTTPException(status_code=404, detail="No existe una cuenta con ese correo.")

    # Simula el código que normalmente llegaría por correo.
    codigo = str(secrets.randbelow(900000) + 100000)
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
        raise HTTPException(status_code=404, detail="No existe esa cuenta.")

    if not usuario["reset_code"] or datos.codigo.strip() != usuario["reset_code"]:
        raise HTTPException(status_code=400, detail="El código de recuperación no es válido.")

    if not datos.nueva_password:
        raise HTTPException(status_code=400, detail="La nueva contraseña es obligatoria.")

    usuario["password_hash"] = hash_password(datos.nueva_password)
    usuario["reset_code"] = None

    return {"mensaje": "Contraseña cambiada correctamente."}
