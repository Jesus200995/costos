from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    tipo_capturista: str
    estado: str
    municipio: int
    localidad: Optional[str] = None
    telefono: Optional[str] = None
    consent: bool = False
    # REPRESENTANTE_CAC
    cac_id: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    # COM_COMERCIALIZACION
    rol_comision: Optional[str] = None
    # OFICINAS
    correo_institucional: Optional[str] = None
    rol_interno: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    avatar: Optional[str] = None
    createdAt: str
    tipo_capturista: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[int] = None
    localidad: Optional[str] = None
    telefono: Optional[str] = None
    consent: bool = False
    cac_id: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    rol_comision: Optional[str] = None
    correo_institucional: Optional[str] = None
    rol_interno: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserPublic
    token: str


class EstadoOut(BaseModel):
    cve_ent: str
    nom_ent: str


class MunicipioOut(BaseModel):
    clave_mun: int
    nomgeo: str
    cve_ent: str
