from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas import (
    CategoriaOut, SubcategoriaOut, ProductoOut, UnidadOut,
    MercadoCreate, MercadoOut, ReporteCreate, ReporteOut, ReporteDetalleOut, DetalleItemOut,
    PrecioIndividualCreate, PrecioHistorialItem
)
from app.database import get_db
from app.auth import get_current_user_id

router = APIRouter()


# ── Catálogos ──

@router.get("/categorias", response_model=List[CategoriaOut])
def list_categorias():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre")
        return [dict(r) for r in cur.fetchall()]


@router.get("/subcategorias", response_model=List[SubcategoriaOut])
def list_subcategorias(categoria_id: str = Query(...)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, categoria_id, nombre FROM subcategorias WHERE categoria_id = %s ORDER BY nombre",
            (categoria_id,),
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/productos", response_model=List[ProductoOut])
def list_productos(subcategoria_id: str = Query(...)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, subcategoria_id, nombre FROM productos WHERE subcategoria_id = %s ORDER BY nombre",
            (subcategoria_id,),
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/unidades", response_model=List[UnidadOut])
def list_unidades(subcategoria_id: str = Query(...), tipo_precio: Optional[str] = Query(None)):
    with get_db() as conn:
        cur = conn.cursor()
        if tipo_precio and tipo_precio in ('MENUDEO', 'MAYOREO'):
            cur.execute(
                "SELECT id, subcategoria_id, nombre FROM unidades_subcategoria WHERE subcategoria_id = %s AND tipo = %s ORDER BY nombre",
                (subcategoria_id, tipo_precio),
            )
        else:
            cur.execute(
                "SELECT DISTINCT ON (subcategoria_id, nombre) id, subcategoria_id, nombre FROM unidades_subcategoria WHERE subcategoria_id = %s ORDER BY subcategoria_id, nombre",
                (subcategoria_id,),
            )
        return [dict(r) for r in cur.fetchall()]


# ── Mercados del usuario ──

@router.get("/", response_model=List[MercadoOut])
def list_mercados(user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, nombre, created_at FROM mercados WHERE user_id = %s::uuid ORDER BY nombre",
            (user_id,),
        )
        rows = cur.fetchall()
    return [MercadoOut(id=r["id"], nombre=r["nombre"], created_at=r["created_at"].isoformat()) for r in rows]


@router.post("/", response_model=MercadoOut, status_code=201)
def create_mercado(data: MercadoCreate, user_id: str = Depends(get_current_user_id)):
    nombre = data.nombre.strip().upper()
    if len(nombre) < 2:
        raise HTTPException(400, "El nombre del mercado debe tener al menos 2 caracteres")
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM mercados WHERE user_id = %s::uuid AND UPPER(nombre) = %s",
            (user_id, nombre),
        )
        if cur.fetchone():
            raise HTTPException(409, "Ya tienes un mercado con ese nombre")
        cur.execute(
            "INSERT INTO mercados (nombre, user_id) VALUES (%s, %s::uuid) RETURNING id, nombre, created_at",
            (nombre, user_id),
        )
        r = cur.fetchone()
    return MercadoOut(id=r["id"], nombre=r["nombre"], created_at=r["created_at"].isoformat())


@router.delete("/{mercado_id}", status_code=204)
def delete_mercado(mercado_id: int, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM mercados WHERE id = %s AND user_id = %s::uuid",
            (mercado_id, user_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "Mercado no encontrado")


# ── Reportes de precios ──

@router.post("/reportes", response_model=ReporteOut, status_code=201)
def create_reporte(data: ReporteCreate, user_id: str = Depends(get_current_user_id)):
    if not data.items:
        raise HTTPException(400, "Debe agregar al menos un producto")
    if data.tipo_precio not in ("MENUDEO", "MAYOREO"):
        raise HTTPException(400, "Tipo de precio inválido")

    seen = set()
    for item in data.items:
        if item.precio <= 0:
            raise HTTPException(400, "El precio debe ser mayor a 0")
        if item.precio != round(item.precio, 2):
            raise HTTPException(400, "El precio debe tener máximo 2 decimales")
        key = (item.producto_id, item.unidad)
        if key in seen:
            raise HTTPException(400, "Producto duplicado con la misma unidad")
        seen.add(key)

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM mercados WHERE id = %s AND user_id = %s::uuid",
            (data.mercado_id, user_id),
        )
        if not cur.fetchone():
            raise HTTPException(404, "Mercado no encontrado")

        cur.execute(
            """INSERT INTO reportes_precios (user_id, mercado_id, tipo_precio)
               VALUES (%s::uuid, %s, %s)
               RETURNING id, fecha, created_at""",
            (user_id, data.mercado_id, data.tipo_precio),
        )
        reporte = cur.fetchone()

        for item in data.items:
            cur.execute(
                """INSERT INTO detalle_precios (reporte_id, producto_id, precio, unidad)
                   VALUES (%s, %s, %s, %s)""",
                (reporte["id"], item.producto_id, item.precio, item.unidad),
            )

    return ReporteOut(
        id=reporte["id"],
        mercado_id=data.mercado_id,
        tipo_precio=data.tipo_precio,
        fecha=reporte["fecha"].isoformat(),
        created_at=reporte["created_at"].isoformat(),
        total_productos=len(data.items),
    )


@router.get("/reportes", response_model=List[ReporteOut])
def list_reportes(user_id: str = Depends(get_current_user_id), mercado_id: Optional[int] = None):
    with get_db() as conn:
        cur = conn.cursor()
        if mercado_id:
            cur.execute(
                """SELECT r.id, r.mercado_id, r.tipo_precio, r.fecha, r.created_at,
                       COUNT(d.id) as total_productos
                   FROM reportes_precios r
                   LEFT JOIN detalle_precios d ON d.reporte_id = r.id
                   WHERE r.user_id = %s::uuid AND r.mercado_id = %s
                   GROUP BY r.id ORDER BY r.created_at DESC""",
                (user_id, mercado_id),
            )
        else:
            cur.execute(
                """SELECT r.id, r.mercado_id, r.tipo_precio, r.fecha, r.created_at,
                       COUNT(d.id) as total_productos
                   FROM reportes_precios r
                   LEFT JOIN detalle_precios d ON d.reporte_id = r.id
                   WHERE r.user_id = %s::uuid
                   GROUP BY r.id ORDER BY r.created_at DESC""",
                (user_id,),
            )
        rows = cur.fetchall()
    return [
        ReporteOut(
            id=r["id"],
            mercado_id=r["mercado_id"],
            tipo_precio=r["tipo_precio"],
            fecha=r["fecha"].isoformat(),
            created_at=r["created_at"].isoformat(),
            total_productos=r["total_productos"],
        )
        for r in rows
    ]


@router.get("/reportes/{reporte_id}", response_model=ReporteDetalleOut)
def get_reporte(reporte_id: int, user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT r.id, r.mercado_id, r.tipo_precio, r.fecha, r.created_at,
                   m.nombre as mercado_nombre
               FROM reportes_precios r
               JOIN mercados m ON m.id = r.mercado_id
               WHERE r.id = %s AND r.user_id = %s::uuid""",
            (reporte_id, user_id),
        )
        reporte = cur.fetchone()
        if not reporte:
            raise HTTPException(404, "Reporte no encontrado")

        cur.execute(
            """SELECT d.id, d.producto_id, p.nombre as producto_nombre,
                   d.precio, d.unidad, p.subcategoria_id
               FROM detalle_precios d
               JOIN productos p ON p.id = d.producto_id
               WHERE d.reporte_id = %s
               ORDER BY p.nombre""",
            (reporte_id,),
        )
        items = cur.fetchall()

    return ReporteDetalleOut(
        id=reporte["id"],
        mercado_id=reporte["mercado_id"],
        mercado_nombre=reporte["mercado_nombre"],
        tipo_precio=reporte["tipo_precio"],
        fecha=reporte["fecha"].isoformat(),
        created_at=reporte["created_at"].isoformat(),
        items=[
            DetalleItemOut(
                id=i["id"],
                producto_id=i["producto_id"],
                producto_nombre=i["producto_nombre"],
                precio=float(i["precio"]),
                unidad=i["unidad"],
                subcategoria_id=i["subcategoria_id"],
            )
            for i in items
        ],
    )


# ── Precio individual (producto por producto) ──

@router.post("/precio", response_model=PrecioHistorialItem, status_code=201)
def create_precio_individual(data: PrecioIndividualCreate, user_id: str = Depends(get_current_user_id)):
    if data.tipo_precio not in ("MENUDEO", "MAYOREO"):
        raise HTTPException(400, "Tipo de precio inválido")
    if data.precio <= 0:
        raise HTTPException(400, "El precio debe ser mayor a 0")
    if data.precio != round(data.precio, 2):
        raise HTTPException(400, "El precio debe tener máximo 2 decimales")

    with get_db() as conn:
        cur = conn.cursor()
        # Verificar mercado pertenece al usuario
        cur.execute(
            "SELECT id FROM mercados WHERE id = %s AND user_id = %s::uuid",
            (data.mercado_id, user_id),
        )
        if not cur.fetchone():
            raise HTTPException(404, "Mercado no encontrado")

        # Verificar producto existe
        cur.execute(
            "SELECT id, subcategoria_id, nombre FROM productos WHERE id = %s",
            (data.producto_id,),
        )
        prod = cur.fetchone()
        if not prod:
            raise HTTPException(404, "Producto no encontrado")

        # Crear reporte de 1 item
        cur.execute(
            """INSERT INTO reportes_precios (user_id, mercado_id, tipo_precio)
               VALUES (%s::uuid, %s, %s)
               RETURNING id, fecha, created_at""",
            (user_id, data.mercado_id, data.tipo_precio),
        )
        reporte = cur.fetchone()

        cur.execute(
            """INSERT INTO detalle_precios (reporte_id, producto_id, precio, unidad)
               VALUES (%s, %s, %s, %s)
               RETURNING id""",
            (reporte["id"], data.producto_id, data.precio, data.unidad),
        )
        detalle = cur.fetchone()

        # Obtener nombre de subcategoría
        cur.execute(
            "SELECT nombre FROM subcategorias WHERE id = %s",
            (prod["subcategoria_id"],),
        )
        sub = cur.fetchone()

    return PrecioHistorialItem(
        id=detalle["id"],
        producto_id=data.producto_id,
        producto_nombre=prod["nombre"],
        subcategoria_nombre=sub["nombre"] if sub else "",
        precio=data.precio,
        unidad=data.unidad,
        tipo_precio=data.tipo_precio,
        fecha=reporte["fecha"].isoformat(),
        created_at=reporte["created_at"].isoformat(),
    )


@router.get("/precios-historial", response_model=List[PrecioHistorialItem])
def list_precios_historial(mercado_id: int = Query(...), user_id: str = Depends(get_current_user_id)):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT d.id, d.producto_id, p.nombre as producto_nombre,
                   s.nombre as subcategoria_nombre,
                   d.precio, d.unidad, r.tipo_precio, r.fecha, r.created_at
               FROM detalle_precios d
               JOIN reportes_precios r ON r.id = d.reporte_id
               JOIN productos p ON p.id = d.producto_id
               JOIN subcategorias s ON s.id = p.subcategoria_id
               WHERE r.mercado_id = %s AND r.user_id = %s::uuid
               ORDER BY r.created_at DESC""",
            (mercado_id, user_id),
        )
        rows = cur.fetchall()
    return [
        PrecioHistorialItem(
            id=r["id"],
            producto_id=r["producto_id"],
            producto_nombre=r["producto_nombre"],
            subcategoria_nombre=r["subcategoria_nombre"],
            precio=float(r["precio"]),
            unidad=r["unidad"],
            tipo_precio=r["tipo_precio"],
            fecha=r["fecha"].isoformat(),
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]
