from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    curp: str
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


class UpdateProfileRequest(BaseModel):
    name: str
    curp: str
    tipo_capturista: str
    estado: str
    municipio: int
    localidad: Optional[str] = None
    telefono: Optional[str] = None
    cac_id: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    rol_comision: Optional[str] = None
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
    curp: Optional[str] = None
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
    territorio: Optional[str] = None


# ── Mercados / Precios ──

class CategoriaOut(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str] = None


class SubcategoriaOut(BaseModel):
    id: str
    categoria_id: str
    nombre: str


class ProductoOut(BaseModel):
    id: int
    subcategoria_id: str
    nombre: str


class UnidadOut(BaseModel):
    id: int
    subcategoria_id: str
    nombre: str


class MercadoCreate(BaseModel):
    nombre: str


class MercadoOut(BaseModel):
    id: int
    nombre: str
    created_at: str


class DetalleItem(BaseModel):
    producto_id: int
    precio: float
    unidad: str


class ReporteCreate(BaseModel):
    mercado_id: int
    tipo_precio: str
    items: List[DetalleItem]


class ReporteOut(BaseModel):
    id: int
    mercado_id: int
    tipo_precio: str
    fecha: str
    created_at: str
    total_productos: int


class DetalleItemOut(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    precio: float
    unidad: str
    subcategoria_id: str


class ReporteDetalleOut(BaseModel):
    id: int
    mercado_id: int
    mercado_nombre: str
    tipo_precio: str
    fecha: str
    created_at: str
    items: List[DetalleItemOut]


# ── Precio individual ──

class PrecioIndividualCreate(BaseModel):
    mercado_id: int
    tipo_precio: str
    producto_id: int
    precio: float
    unidad: str


class PrecioHistorialItem(BaseModel):
    id: int
    producto_id: int
    producto_nombre: str
    subcategoria_nombre: str
    precio: float
    unidad: str
    tipo_precio: str
    fecha: str
    created_at: str
