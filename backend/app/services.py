from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import ALGORITHM, SECRET_KEY, TOKEN_EXPIRE_HOURS

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.database import usuarios

security = HTTPBearer(auto_error=False)



# funciones de email y contraseñas

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


# funciones de jwt

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


def obtener_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(security)):
    
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="debes iniciar sesion",
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
                detail="sesion no válida"
            )

        return usuarios[email]

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token invalido o expirado"
        )