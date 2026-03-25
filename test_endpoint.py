import sys, json
sys.path.insert(0, '/var/www/costos/backend')
from app.database import get_db

with get_db() as conn:
    cur = conn.cursor()
    
    # Test mercado autorizado
    cur.execute(
        "SELECT m.id, m.nombre, m.latitud, m.longitud, cm.entidad, cm.municipio, cm.localidad, cm.tipo AS tipo_mercado "
        "FROM mercados m LEFT JOIN catalogo_mercados cm ON cm.id = m.catalogo_mercado_id WHERE m.id = 7"
    )
    row = cur.fetchone()
    mercado = dict(row) if row else None
    print('MERCADO:', mercado)
    print('MERCADO TYPES:', {k: type(v).__name__ for k, v in mercado.items()} if mercado else 'None')
    
    # Test precios
    cur.execute(
        "SELECT dp.id, p.nombre AS producto, dp.precio, dp.unidad, rp.tipo_precio, rp.fecha, rp.created_at, "
        "u.nombre || ' ' || u.apellido_paterno AS capturista "
        "FROM detalle_precios dp "
        "JOIN reportes_precios rp ON rp.id = dp.reporte_id "
        "JOIN productos p ON p.id = dp.producto_id "
        "JOIN users u ON u.id = rp.user_id "
        "WHERE rp.mercado_id = 7 ORDER BY rp.created_at DESC LIMIT 5"
    )
    precios = []
    for r in cur.fetchall():
        d = dict(r)
        d["fecha"] = d["fecha"].isoformat() if d["fecha"] else None
        d["created_at"] = d["created_at"].isoformat() if d["created_at"] else None
        d["precio"] = float(d["precio"])
        precios.append(d)
        
    print('PRECIOS:', precios)
    
    # Try JSON serialization
    try:
        result = {"mercado": mercado, "precios": precios}
        print('JSON:', json.dumps(result, default=str))
    except Exception as e:
        print('JSON ERROR:', e)
