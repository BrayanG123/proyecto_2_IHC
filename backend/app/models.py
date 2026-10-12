from datetime import date
from pydantic import BaseModel


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
    nuevo_password: str
    

class SesionDeEstudio(BaseModel):
    nombre: str
    fecha: date
    modalidad: str
    cupo: str
    inscripciones: bool