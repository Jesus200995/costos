from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from app.database import get_db
from app.auth import hash_password, verify_password, create_token
import re, hashlib, uuid
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


class AdminUserUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    curp: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    rol: Optional[str] = None


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


@router.put("/usuarios/{user_id}", response_model=AdminUserListOut)
def update_usuario(user_id: int, data: AdminUserUpdateRequest, token: str):
    """Actualizar campos de usuario administrativo (solo administradores)"""
    admin_id = require_admin(token)

    updates = data.dict(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No se proporcionaron campos para actualizar")

    # No permitir cambiar rol propio a usuario
    if user_id == admin_id and updates.get("rol") == "usuario":
        raise HTTPException(400, "No puedes quitarte el rol de administrador")

    set_parts = []
    values = []
    for field, value in updates.items():
        set_parts.append(f"{field} = %s")
        values.append(value)
    values.append(user_id)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""UPDATE usersadmin SET {', '.join(set_parts)}, updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
               RETURNING id, nombre, apellido_paterno, apellido_materno, curp, correo, telefono,
                         rol, estatus, created_at""",
            values,
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


class PWAUserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
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
    correo_institucional: Optional[str] = None
    rol_interno: Optional[str] = None


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


@router.put("/usuarios-pwa/{user_id}", response_model=PWAUserOut)
def update_usuario_pwa(user_id: str, data: PWAUserUpdateRequest, token: str):
    """Actualizar usuario PWA (solo administradores)"""
    require_admin(token)

    # Build SET clause dynamically from provided fields
    updates = data.dict(exclude_unset=True)
    if not updates:
        raise HTTPException(400, "No se proporcionaron campos para actualizar")

    set_parts = []
    values = []
    for field, value in updates.items():
        set_parts.append(f"{field} = %s")
        values.append(value)
    values.append(user_id)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""UPDATE users SET {', '.join(set_parts)}, updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
               RETURNING id, name, email, curp, tipo_capturista, estado, municipio,
                         localidad, telefono, cac_id, cac_nombre, territorio, ruta,
                         rol_comision, correo_institucional, rol_interno, created_at""",
            values,
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return PWAUserOut(
        id=str(row["id"]),
        name=row["name"],
        email=row["email"],
        curp=row["curp"],
        tipo_capturista=row["tipo_capturista"],
        estado=row["estado"],
        municipio=row["municipio"],
        localidad=row["localidad"],
        telefono=row["telefono"],
        cac_id=row["cac_id"],
        cac_nombre=row["cac_nombre"],
        territorio=row["territorio"],
        ruta=row["ruta"],
        rol_comision=row["rol_comision"],
        correo_institucional=row["correo_institucional"],
        rol_interno=row["rol_interno"],
        created_at=row["created_at"].isoformat(),
    )


@router.delete("/usuarios-pwa/{user_id}")
def delete_usuario_pwa(user_id: str, token: str):
    """Eliminar usuario PWA (solo administradores)"""
    require_admin(token)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Usuario no encontrado")

    return {"message": "Usuario PWA eliminado correctamente"}


# ═══════════════════════════════════════════════════════════════════
# MERCADOS PROPUESTOS — GESTIÓN ADMIN
# ═══════════════════════════════════════════════════════════════════

class MercadoPropuestoAdminOut(BaseModel):
    id: int
    nombre_mercado: str
    tipo_mercado: str
    tipo_mercado_otro: Optional[str] = None
    estado: str
    municipio: str
    localidad_colonia: Optional[str] = None
    latitud: float
    longitud: float
    dias_operacion: List[str]
    horario: Optional[str] = None
    referencia: Optional[str] = None
    observaciones: Optional[str] = None
    status: str
    created_by: str
    created_by_nombre: Optional[str] = None
    tipo_capturista: Optional[str] = None
    cac_nombre: Optional[str] = None
    territorio: Optional[str] = None
    ruta: Optional[str] = None
    created_at: str


@router.get("/propuestas", response_model=List[MercadoPropuestoAdminOut])
def list_propuestas(token: str, status: Optional[str] = None):
    """Listar mercados propuestos (solo administradores)"""
    require_admin(token)

    with get_db() as conn:
        cur = conn.cursor()
        query = """SELECT mp.id, mp.nombre_mercado, mp.tipo_mercado, mp.tipo_mercado_otro,
                          mp.estado, mp.municipio, mp.localidad_colonia,
                          mp.latitud, mp.longitud, mp.dias_operacion,
                          mp.horario, mp.referencia, mp.observaciones,
                          mp.status, mp.created_by, mp.tipo_capturista,
                          mp.cac_nombre, mp.territorio, mp.ruta, mp.created_at,
                          u.name AS created_by_nombre
                   FROM mercados_propuestos mp
                   LEFT JOIN users u ON u.id = mp.created_by"""
        params = []
        if status:
            query += " WHERE mp.status = %s"
            params.append(status)
        query += " ORDER BY mp.created_at DESC"
        cur.execute(query, params)
        rows = cur.fetchall()

    return [
        MercadoPropuestoAdminOut(
            id=r["id"],
            nombre_mercado=r["nombre_mercado"],
            tipo_mercado=r["tipo_mercado"],
            tipo_mercado_otro=r["tipo_mercado_otro"],
            estado=r["estado"],
            municipio=r["municipio"],
            localidad_colonia=r["localidad_colonia"],
            latitud=r["latitud"],
            longitud=r["longitud"],
            dias_operacion=r["dias_operacion"],
            horario=r["horario"],
            referencia=r["referencia"],
            observaciones=r["observaciones"],
            status=r["status"],
            created_by=str(r["created_by"]),
            created_by_nombre=r["created_by_nombre"],
            tipo_capturista=r["tipo_capturista"],
            cac_nombre=r["cac_nombre"],
            territorio=r["territorio"],
            ruta=r["ruta"],
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]


@router.patch("/propuestas/{propuesta_id}/autorizar")
def autorizar_propuesta(propuesta_id: int, token: str):
    """Autorizar mercado propuesto: lo agrega al catálogo y marca como autorizado"""
    require_admin(token)

    with get_db() as conn:
        cur = conn.cursor()

        # Obtener la propuesta
        cur.execute(
            """SELECT id, nombre_mercado, tipo_mercado, estado, municipio,
                      localidad_colonia, latitud, longitud, status
               FROM mercados_propuestos WHERE id = %s""",
            (propuesta_id,),
        )
        prop = cur.fetchone()
        if not prop:
            raise HTTPException(404, "Propuesta no encontrada")
        if prop["status"] != "pendiente_autorizacion":
            raise HTTPException(400, f"La propuesta ya fue {prop['status']}")

        # Generar market_id único
        raw = f"{prop['nombre_mercado']}-{prop['estado']}-{prop['municipio']}-{uuid.uuid4().hex[:8]}"
        market_id = "mkt_" + hashlib.md5(raw.encode()).hexdigest()[:10]

        # Mapeo de tipos
        tipo_map = {
            "MERCADO_PUBLICO": "MERCADO PÚBLICO",
            "TIANGUIS": "TIANGUIS",
            "CENTRAL_ABASTO": "CENTRAL DE ABASTO",
            "OTRO": "OTRO",
        }
        tipo = tipo_map.get(prop["tipo_mercado"], prop["tipo_mercado"])

        # Insertar en catalogo_mercados
        cur.execute(
            """INSERT INTO catalogo_mercados
                   (market_id, nombre, tipo, entidad, municipio, localidad, latitud, longitud)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (
                market_id,
                prop["nombre_mercado"],
                tipo,
                prop["estado"],
                prop["municipio"],
                prop["localidad_colonia"],
                prop["latitud"],
                prop["longitud"],
            ),
        )
        cat_row = cur.fetchone()

        # Marcar propuesta como autorizada
        cur.execute(
            "UPDATE mercados_propuestos SET status = 'autorizado', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (propuesta_id,),
        )

    return {
        "message": "Mercado autorizado y agregado al catálogo",
        "catalogo_id": cat_row["id"],
        "market_id": market_id,
    }


@router.patch("/propuestas/{propuesta_id}/rechazar")
def rechazar_propuesta(propuesta_id: int, token: str):
    """Rechazar mercado propuesto"""
    require_admin(token)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status FROM mercados_propuestos WHERE id = %s", (propuesta_id,))
        prop = cur.fetchone()
        if not prop:
            raise HTTPException(404, "Propuesta no encontrada")
        if prop["status"] != "pendiente_autorizacion":
            raise HTTPException(400, f"La propuesta ya fue {prop['status']}")

        cur.execute(
            "UPDATE mercados_propuestos SET status = 'rechazado', updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (propuesta_id,),
        )

    return {"message": "Propuesta rechazada"}


# ═══════════════════════════════════════════════════════════════════
# REGISTROS DE PRECIOS (todos los usuarios)
# ═══════════════════════════════════════════════════════════════════

@router.get("/registros-precios")
def list_registros_precios(
    token: str,
    fecha_desde: Optional[str] = Query(None),
    fecha_hasta: Optional[str] = Query(None),
    producto: Optional[str] = Query(None),
    mercado: Optional[str] = Query(None),
    tipo_precio: Optional[str] = Query(None),
    usuario: Optional[str] = Query(None),
):
    require_admin(token)

    with get_db() as conn:
        cur = conn.cursor()
        query = """
            SELECT d.id, r.user_id, u.name AS user_name, u.email AS user_email,
                   r.mercado_id, cm.nombre AS mercado_nombre,
                   cm.entidad AS mercado_entidad, cm.municipio AS mercado_municipio,
                   d.producto_id, p.nombre AS producto_nombre,
                   s.nombre AS subcategoria_nombre, s.categoria_id,
                   d.precio, d.unidad, r.tipo_precio, r.fecha, r.created_at
            FROM detalle_precios d
            JOIN reportes_precios r ON r.id = d.reporte_id
            JOIN productos p ON p.id = d.producto_id
            JOIN subcategorias s ON s.id = p.subcategoria_id
            JOIN mercados m ON m.id = r.mercado_id
            JOIN catalogo_mercados cm ON cm.id = m.catalogo_mercado_id
            JOIN users u ON u.id = r.user_id
            WHERE 1=1
        """
        params: list = []

        if fecha_desde:
            query += " AND r.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND r.fecha <= %s"
            params.append(fecha_hasta)
        if producto:
            query += " AND LOWER(p.nombre) LIKE LOWER(%s)"
            params.append(f"%{producto}%")
        if mercado:
            query += " AND LOWER(cm.nombre) LIKE LOWER(%s)"
            params.append(f"%{mercado}%")
        if tipo_precio:
            query += " AND r.tipo_precio = %s"
            params.append(tipo_precio)
        if usuario:
            query += " AND (LOWER(u.name) LIKE LOWER(%s) OR LOWER(u.email) LIKE LOWER(%s))"
            params.append(f"%{usuario}%")
            params.append(f"%{usuario}%")

        query += " ORDER BY r.created_at DESC"
        cur.execute(query, params)
        rows = cur.fetchall()

    return [
        {
            "id": r["id"],
            "user_id": str(r["user_id"]),
            "user_name": r["user_name"],
            "user_email": r["user_email"],
            "mercado_id": r["mercado_id"],
            "mercado_nombre": r["mercado_nombre"],
            "mercado_entidad": r["mercado_entidad"],
            "mercado_municipio": r["mercado_municipio"],
            "producto_id": r["producto_id"],
            "producto_nombre": r["producto_nombre"],
            "subcategoria_nombre": r["subcategoria_nombre"],
            "categoria_id": r["categoria_id"],
            "precio": float(r["precio"]),
            "unidad": r["unidad"],
            "tipo_precio": r["tipo_precio"],
            "fecha": r["fecha"].isoformat(),
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]
