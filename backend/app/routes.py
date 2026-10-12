import secrets

from fastapi import APIRouter, Depends, HTTPException, status

from app.models import CambiarPassword, SesionDeEstudio, Login, RecuperarPassword, Registro
from app.services import crear_token, hash_password, normalizar_email, obtener_usuario_actual, verificar_password
# from main import obtener_usuario_actual

from app.database import usuarios, sesiones
# from app.models import Registro



router = APIRouter()


@router.post("/registro")
def registrar_usuario(data: Registro):
    email = normalizar_email(data.email)

    if not data.nombre.strip():
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio."
        )

    if not email or "@" not in email:
        raise HTTPException(
            status_code=400,
            detail="Ingresa un correo válido."
        )

    if not data.password:
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
        "nombre": data.nombre.strip(),
        "email": email,
        "password_hash": hash_password(data.password),
        "reset_code": None,
    }

    return {
        "mensaje": "cuenta creada exitosamente"
    }


@router.post("/login")
def iniciar_sesion(data: Login):

    email = normalizar_email(data.email)
    usuario = usuarios.get(email)

    if not usuario or not verificar_password(
        data.password,
        usuario["password_hash"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )

    token = crear_token(email)

    return {
        "mensaje": "incio de sesion correcto",
        "token": token,
        "usuario": {
            "nombre": usuario["nombre"],
            "email": usuario["email"],
        },
    }


@router.get("/perfil")
def perfil(usuario=Depends(obtener_usuario_actual)):
    return {
        "nombre": usuario["nombre"],
        "email": usuario["email"],
    }


@router.post("/logout")
def cerrar_sesion(usuario=Depends(obtener_usuario_actual)):
    return {
        "mensaje": "sesion cerrada correctamente"
    }



# recuperacion de contraseñas

@router.post("/recuperar-password")
def recuperar_password(data: RecuperarPassword):

    email = normalizar_email(datos.email)
    usuario = usuarios.get(email)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="No existe una cuenta con ese correo."
        )

    # simular codigo de recuperacion
    codigo = str(
        secrets.randbelow(900000) + 100000
    )

    usuario["reset_code"] = codigo

    return {
        "mensaje": "Código de recuperación generado.",
        "codigo": codigo,
        "nota": "En un sistema real, este código se enviaría por correo.",
    }


@router.post("/cambiar-password")
def cambiar_password(data: CambiarPassword):
    email = normalizar_email(data.email)
    usuario = usuarios.get(email)

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="No existe esa cuenta"
        )
    
    if (
        not usuario["reset_code"]
        or data.codigo.strip() != usuario["reset_code"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Codigo de recuperacion no valido"
        )

    if not data.nuevo_password:
        raise HTTPException(
            status_code=400,
            detail="El nuevo password es obligatorio"
        )

    usuario["password_hash"] = hash_password(
        data.nuevo_password
    )

    usuario["reset_code"] = None

    return {
        "mensaje": "contraseña cambiada con exito"
    }


@router.post("/guardar-nuevo")
def crear_sesion(data: SesionDeEstudio):

    nombre = data.nombre.strip()

    if not data.nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre es obligatorio."
        )

    if not data.fecha:
        raise HTTPException(
            status_code=400,
            detail="El fecha es obligatorio."
        )

    if not data.cupo:
        raise HTTPException(
            status_code=400,
            detail="el cupo es obligatorio."
        )
    
    if not data.inscripciones:
        raise HTTPException(
            status_code=400,
            detail="debes definir el estado de las inscripciones."
        )

    sesiones[nombre] = {
        "nombre": nombre,
        "fecha": data.fecha,
        "modalidad": data.modalidad,
        "cupo": data.cupo,
        "inscripciones": data.inscripciones
    }

    return {
        "mensaje": "sesion de estudio registrada correctamente"
    }


@router.post("/cerrar-inscripciones")
def cerrar_inscripciones(data: SesionDeEstudio):

    
    sesiones[data.nombre].update({
        "inscripciones": data.inscripciones
    })

    
    return {
        "mensaje": "estado de inscripciones modificada correctamente"
    }
