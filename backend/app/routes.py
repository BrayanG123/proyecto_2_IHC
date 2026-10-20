import secrets
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CambiarPassword, SesionDeEstudio, Login, RecuperarPassword, Registro

from app.repositorio import (
    cerrar_inscripciones as cerrar_inscripciones_db,
    get_user_by_email,
    guardar_sesion,
    guardar_usuario,
    listar_sesiones,
    buscar_sesiones,
    unirse_a_sesion,
)

from app.services import (
    crear_token, 
    hash_password, 
    normalizar_email,
    obtener_usuario_actual, 
    verificar_password,
)

router = APIRouter()


def validar_password(password):
    
    if not password:
        raise HTTPException(
            status_code=400, 
            detail="La contraseña es obligatoria"
        )
    
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400, 
            detail="La contraseña admite hasta 72 bytes."
        )


@router.post("/registro")
def registrar_usuario(data: Registro, db: Session = Depends(get_db)):

    email = normalizar_email(data.email)

    if not data.nombre.strip():
        raise HTTPException(
            status_code=400, 
            detail="El nombre es obligatorio."
        )
    
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Ingresa un correo válido.")
    
    validar_password(data.password)

    if get_user_by_email(db, email):
        raise HTTPException(status_code=409, detail="El correo ya está registrado.")
    
    try:
        usuario = guardar_usuario(db, data.nombre, email, hash_password(data.password))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="El correo ya está registrado.")
    
    return {"mensaje": "Cuenta registrada correctamente.", "id": usuario.id}


@router.post("/login")
def iniciar_sesion(data: Login, db: Session = Depends(get_db)):

    email = normalizar_email(data.email)
    usuario = get_user_by_email(db, email)

    if not usuario or not verificar_password(data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
        )
    
    return {
        "mensaje": "Inicio de sesión correcto.",
        "token": crear_token(email),
        "usuario": {"nombre": usuario.nombre, "email": usuario.email},
    }


@router.get("/perfil")
def perfil(usuario=Depends(obtener_usuario_actual)):

    return {"nombre": usuario.nombre, "email": usuario.email}


@router.get("/all-sesions")
def get_all_sesions(
    nombre: str = "",
    materia: str = "",
    modalidad: Literal["", "presencial", "virtual"] = "",
    periodo: Literal["", "hoy", "proximos7", "rango"] = "",
    desde: date | None = None,
    hasta: date | None = None,
    disponible: bool = False,
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual),
):
    
    try:
        return buscar_sesiones(db, usuario.id, nombre, materia, modalidad,
                               periodo, desde, hasta, disponible)
    except ValueError as error:
        raise HTTPException(
            status_code=400, 
            detail=str(error)
        )



@router.get("/materias")
def get_materias(db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):

    return sorted(
        {sesion.materia for sesion in listar_sesiones(db)}, 
        key=str.casefold
    )


@router.post("/sesiones/{sesion_id}/inscribirse")
def inscribirse(
    sesion_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual),
):
    try:
        unirse_a_sesion(db, sesion_id, usuario.id)
    except ValueError as error:
        raise HTTPException(
            status_code=400, 
            detail=str(error)
        )
    
    return {"mensaje": "Te inscribiste en la sesión correctamente."}


@router.post("/logout")
def cerrar_sesion(usuario=Depends(obtener_usuario_actual)):
    return {"mensaje": "Sesión cerrada correctamente."}


@router.post("/recuperar-password")
def recuperar_password(data: RecuperarPassword, db: Session = Depends(get_db)):

    usuario = get_user_by_email(db, normalizar_email(data.email))

    if not usuario:
        raise HTTPException(
            status_code=404, detail="No existe una cuenta con ese correo"
        )
    
    codigo = str(secrets.randbelow(900000) + 100000)
    usuario.reset_code = codigo
    db.commit()

    return {
        "mensaje": "Código de recuperación generado.",
        "codigo": codigo,
        "nota": "En un sistema real, este código se enviaría por correo.",
    }


@router.post("/cambiar-password")
def cambiar_password(data: CambiarPassword, db: Session = Depends(get_db)):

    usuario = get_user_by_email(db, normalizar_email(data.email))
    
    if not usuario:
        raise HTTPException(
            status_code=404, 
            detail="No existe esa cuenta"
        )
    
    if not usuario.reset_code or not secrets.compare_digest(data.codigo.strip(), usuario.reset_code):
        raise HTTPException(
            status_code=400, 
            detail="Código de recuperación no valido"
        )
    
    validar_password(data.nueva_password)
    usuario.password_hash = hash_password(data.nueva_password)
    usuario.reset_code = ""
    db.commit()

    return {"mensaje": "Contraseña cambiada correctamente."}


@router.post("/guardar-nuevo")
def crear_sesion(
    data: SesionDeEstudio,
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual),
):
    sesion = guardar_sesion(
        db=db,
        nombre=data.nombre,
        materia=data.materia,
        fecha=data.fecha,
        modalidad=data.modalidad,
        cupo=data.cupo,
        abiertas=data.inscripciones,
        usuario_id=usuario.id,
    )

    return {"mensaje": "Sesión de estudio registrada correctamente.", "id": sesion.id}


@router.post("/cerrar-inscripciones")
def cerrar_inscripciones(
    data: SesionDeEstudio,
    db: Session = Depends(get_db),
    usuario=Depends(obtener_usuario_actual),
):
    coincidencias = [s for s in listar_sesiones(db) if s.nombre == data.nombre and s.usuario_id == usuario.id]

    if len(coincidencias) != 1:
        raise HTTPException(
            status_code=400, 
            detail="No se encontró una sesión única de este usuario."
        )
    
    try:
        cerrar_inscripciones_db(db, coincidencias[0].id, usuario.id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
    return {"mensaje": "Estado de inscripciones modificado correctamente."}
