from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from app.database import get_db
from app.auth import hash_password, verify_password, create_token
import re
import jwt
from app.config import settings

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════

class AdminRegisterRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido_paterno: str = Field(..., min_length=2, max_length=100)
    apellido_materno: str = Field(..., min_length=2, max_length=100)
    curp: str = Field(..., min_length=18, max_length=18)
    correo: EmailStr
    telefono: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=6)
    rol: Optional[str] = Field('usuario', pattern='^(usuario|administrador)$')

    @validator('nombre', 'apellido_paterno', 'apellido_materno', pre=True)
    def normalize_name(cls, v):
        if v:
            # Quitar tildes y convertir a mayúsculas
            import unicodedata
            normalized = unicodedata.normalize('NFD', v)
            without_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
            return without_accents.upper().strip()
        return v

    @validator('curp', pre=True)
    def normalize_curp(cls, v):
        if v:
            return v.upper().strip()
        return v

    @validator('curp')
    def validate_curp(cls, v):
        if not re.match(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$', v):
            raise ValueError('CURP inválida')
        return v

    @validator('telefono')
    def validate_telefono(cls, v):
        if not re.match(r'^\d{10}$', v):
            raise ValueError('El teléfono debe tener exactamente 10 dígitos')
        return v


class AdminLoginRequest(BaseModel):
    correo: EmailStr
    password: str


class AdminUserOut(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    curp: str
    correo: str
    telefono: str
    rol: str
    estatus: str
    created_at: str


class AdminAuthResponse(BaseModel):
    user: AdminUserOut
    token: str


class AdminUserListOut(BaseModel):
    id: int
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    curp: str
    correo: str
    telefono: str
    rol: str
    estatus: str
    created_at: str


class UpdateEstatusRequest(BaseModel):
    estatus: str = Field(..., pattern='^(activo|inactivo)$')


class UpdateRolRequest(BaseModel):
    rol: str = Field(..., pattern='^(usuario|administrador)$')


# ═══════════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════════

def get_current_admin_id(token: str) -> int:
    """Decodifica token y retorna admin_id"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        uid = payload.get("userId") or payload.get("sub")
        return int(uid)
    except:
        raise HTTPException(401, "Token inválido")


def require_admin(token: str = None):
    """Middleware para verificar que el usuario es administrador"""
    if not token:
        raise HTTPException(401, "Token requerido")
    
    admin_id = get_current_admin_id(token)
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT rol, estatus FROM usersadmin WHERE id = %s", (admin_id,))
        row = cur.fetchone()
        
        if not row:
            raise HTTPException(401, "Usuario no encontrado")
        if row["estatus"] != "activo":
            raise HTTPException(403, "Usuario inactivo")
        if row["rol"] != "administrador":
            raise HTTPException(403, "Se requiere rol de administrador")
    
    return admin_id


# ═══════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@router.post("/register", response_model=AdminAuthResponse, status_code=201)
def admin_register(data: AdminRegisterRequest):
    """Registro de usuario administrativo"""
    with get_db() as conn:
        cur = conn.cursor()

        # Verificar CURP duplicada
        cur.execute("SELECT id FROM usersadmin WHERE curp = %s", (data.curp,))
        if cur.fetchone():
            raise HTTPException(409, "Esta CURP ya está registrada")

        # Verificar correo duplicado
        cur.execute("SELECT id FROM usersadmin WHERE correo = %s", (data.correo.lower(),))
        if cur.fetchone():
            raise HTTPException(409, "Este correo ya está registrado")

        hashed = hash_password(data.password)
        rol = data.rol if data.rol in ('usuario', 'administrador') else 'usuario'
        cur.execute(
            """INSERT INTO usersadmin (nombre, apellido_paterno, apellido_materno, curp, correo, telefono, password_hash, rol, estatus)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'activo')
               RETURNING id, nombre, apellido_paterno, apellido_materno, curp, correo, telefono, rol, estatus, created_at""",
            (
                data.nombre,
                data.apellido_paterno,
                data.apellido_materno,
                data.curp,
                data.correo.lower(),
                data.telefono,
                hashed,
                rol,
            ),
        )
        row = cur.fetchone()

    user = AdminUserOut(
        id=row["id"],
        nombre=row["nombre"],
        apellido_paterno=row["apellido_paterno"],
        apellido_materno=row["apellido_materno"],
        curp=row["curp"],
        correo=row["correo"],
        telefono=row["telefono"],
        rol=row["rol"],
        estatus=row["estatus"],
        created_at=row["created_at"].isoformat(),
    )
    token = create_token(str(user.id))
    return AdminAuthResponse(user=user, token=token)


@router.post("/login", response_model=AdminAuthResponse)
def admin_login(data: AdminLoginRequest):
    """Login de usuario administrativo"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre, apellido_paterno, apellido_materno, curp, correo, telefono, 
                      password_hash, rol, estatus, created_at
               FROM usersadmin WHERE correo = %s""",
            (data.correo.lower(),),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(401, "Credenciales incorrectas")

    if not verify_password(data.password, row["password_hash"]):
        raise HTTPException(401, "Credenciales incorrectas")

    if row["estatus"] != "activo":
        raise HTTPException(403, "Tu cuenta está inactiva. Contacta al administrador.")

    user = AdminUserOut(
        id=row["id"],
        nombre=row["nombre"],
        apellido_paterno=row["apellido_paterno"],
        apellido_materno=row["apellido_materno"],
        curp=row["curp"],
        correo=row["correo"],
        telefono=row["telefono"],
        rol=row["rol"],
        estatus=row["estatus"],
        created_at=row["created_at"].isoformat(),
    )
    token = create_token(str(user.id))
    return AdminAuthResponse(user=user, token=token)


@router.get("/me", response_model=AdminUserOut)
def get_current_admin(token: str):
    """Obtener usuario actual"""
    admin_id = get_current_admin_id(token)
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre, apellido_paterno, apellido_materno, curp, correo, telefono, 
                      rol, estatus, created_at
               FROM usersadmin WHERE id = %s""",
            (admin_id,),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return AdminUserOut(
        id=row["id"],
        nombre=row["nombre"],
        apellido_paterno=row["apellido_paterno"],
        apellido_materno=row["apellido_materno"],
        curp=row["curp"],
        correo=row["correo"],
        telefono=row["telefono"],
        rol=row["rol"],
        estatus=row["estatus"],
        created_at=row["created_at"].isoformat(),
    )


@router.get("/usuarios", response_model=List[AdminUserListOut])
def list_usuarios(token: str):
    """Listar todos los usuarios (solo administradores)"""
    require_admin(token)
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, nombre, apellido_paterno, apellido_materno, curp, correo, telefono, 
                      rol, estatus, created_at
               FROM usersadmin ORDER BY created_at DESC"""
        )
        rows = cur.fetchall()

    return [
        AdminUserListOut(
            id=r["id"],
            nombre=r["nombre"],
            apellido_paterno=r["apellido_paterno"],
            apellido_materno=r["apellido_materno"],
            curp=r["curp"],
            correo=r["correo"],
            telefono=r["telefono"],
            rol=r["rol"],
            estatus=r["estatus"],
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]


@router.patch("/usuarios/{user_id}/estatus", response_model=AdminUserListOut)
def update_estatus(user_id: int, data: UpdateEstatusRequest, token: str):
    """Actualizar estatus de usuario (solo administradores)"""
    admin_id = require_admin(token)
    
    # No permitir desactivarse a sí mismo
    if user_id == admin_id and data.estatus == "inactivo":
        raise HTTPException(400, "No puedes desactivarte a ti mismo")
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE usersadmin SET estatus = %s, updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
               RETURNING id, nombre, apellido_paterno, apellido_materno, curp, correo, telefono, 
                         rol, estatus, created_at""",
            (data.estatus, user_id),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return AdminUserListOut(
        id=row["id"],
        nombre=row["nombre"],
        apellido_paterno=row["apellido_paterno"],
        apellido_materno=row["apellido_materno"],
        curp=row["curp"],
        correo=row["correo"],
        telefono=row["telefono"],
        rol=row["rol"],
        estatus=row["estatus"],
        created_at=row["created_at"].isoformat(),
    )


@router.patch("/usuarios/{user_id}/rol", response_model=AdminUserListOut)
def update_rol(user_id: int, data: UpdateRolRequest, token: str):
    """Actualizar rol de usuario (solo administradores)"""
    admin_id = require_admin(token)
    
    # No permitir quitarse el rol de admin a sí mismo
    if user_id == admin_id and data.rol == "usuario":
        raise HTTPException(400, "No puedes quitarte el rol de administrador")
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE usersadmin SET rol = %s, updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
               RETURNING id, nombre, apellido_paterno, apellido_materno, curp, correo, telefono, 
                         rol, estatus, created_at""",
            (data.rol, user_id),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return AdminUserListOut(
        id=row["id"],
        nombre=row["nombre"],
        apellido_paterno=row["apellido_paterno"],
        apellido_materno=row["apellido_materno"],
        curp=row["curp"],
        correo=row["correo"],
        telefono=row["telefono"],
        rol=row["rol"],
        estatus=row["estatus"],
        created_at=row["created_at"].isoformat(),
    )


@router.delete("/usuarios/{user_id}")
def delete_usuario(user_id: int, token: str):
    """Eliminar usuario (solo administradores)"""
    admin_id = require_admin(token)
    
    if user_id == admin_id:
        raise HTTPException(400, "No puedes eliminarte a ti mismo")
    
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM usersadmin WHERE id = %s RETURNING id", (user_id,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return {"message": "Usuario eliminado correctamente"}


# ═══════════════════════════════════════════════════════════════════
# USUARIOS PWA (tabla users)
# ═══════════════════════════════════════════════════════════════════

class PWAUserOut(BaseModel):
    id: str
    name: str
    email: str
    curp: Optional[str] = None
    tipo_capturista: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[int] = None
    localidad: Optional[str] = None
    telefono: Optional[str] = None
    cac_id: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    ruta: Optional[str] = None
    rol_comision: Optional[str] = None
    correo_institucional: Optional[str] = None
    rol_interno: Optional[str] = None
    created_at: str


@router.get("/usuarios-pwa", response_model=List[PWAUserOut])
def list_usuarios_pwa(token: str):
    """Listar todos los usuarios de la PWA (solo administradores)"""
    require_admin(token)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT id, name, email, curp, tipo_capturista, estado, municipio,
                      localidad, telefono, cac_id, cac_nombre, territorio, ruta,
                      rol_comision, correo_institucional, rol_interno, created_at
               FROM users ORDER BY created_at DESC"""
        )
        rows = cur.fetchall()

    return [
        PWAUserOut(
            id=str(r["id"]),
            name=r["name"],
            email=r["email"],
            curp=r["curp"],
            tipo_capturista=r["tipo_capturista"],
            estado=r["estado"],
            municipio=r["municipio"],
            localidad=r["localidad"],
            telefono=r["telefono"],
            cac_id=r["cac_id"],
            cac_nombre=r["cac_nombre"],
            territorio=r["territorio"],
            ruta=r["ruta"],
            rol_comision=r["rol_comision"],
            correo_institucional=r["correo_institucional"],
            rol_interno=r["rol_interno"],
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]
