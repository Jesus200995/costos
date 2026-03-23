export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt: string
  curp?: string
  tipo_capturista?: string
  estado?: string
  municipio?: number
  localidad?: string
  telefono?: string
  consent?: boolean
  cac_id?: string
  cac_nombre?: string
  territorio?: string
  rol_comision?: string
  correo_institucional?: string
  rol_interno?: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
  confirmPassword: string
  curp: string
  tipo_capturista: string
  estado: string
  municipio: number
  localidad?: string
  telefono?: string
  consent: boolean
  cac_id?: string
  cac_nombre?: string
  territorio?: string
  rol_comision?: string
  correo_institucional?: string
  rol_interno?: string
}

export interface AuthResponse {
  user: User
  token: string
}

export interface ApiError {
  message: string
  errors?: Record<string, string[]>
}

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

export interface Estado {
  cve_ent: string
  nom_ent: string
}

export interface Municipio {
  clave_mun: number
  nomgeo: string
  cve_ent: string
  territorio?: string | null
}

// ── Mercados / Precios ──

export interface Categoria {
  id: string
  nombre: string
  descripcion?: string
}

export interface Subcategoria {
  id: string
  categoria_id: string
  nombre: string
}

export interface Producto {
  id: number
  subcategoria_id: string
  nombre: string
}

export interface Unidad {
  id: number
  subcategoria_id: string
  nombre: string
}

export interface Mercado {
  id: number
  nombre: string
  created_at: string
}

export interface DetalleItem {
  producto_id: number
  precio: number
  unidad: string
}

export interface ReporteOut {
  id: number
  mercado_id: number
  tipo_precio: string
  fecha: string
  created_at: string
  total_productos: number
}

export interface DetalleItemOut {
  id: number
  producto_id: number
  producto_nombre: string
  precio: number
  unidad: string
  subcategoria_id: string
}

export interface ReporteDetalleOut {
  id: number
  mercado_id: number
  mercado_nombre: string
  tipo_precio: string
  fecha: string
  created_at: string
  items: DetalleItemOut[]
}

export interface CapturaItem {
  producto_id: number
  producto_nombre: string
  subcategoria_id: string
  categoria_id: string
  precio: number | null
  unidad: string
  unidades_disponibles: string[]
}

export interface PrecioHistorialItem {
  id: number
  producto_id: number
  producto_nombre: string
  subcategoria_nombre: string
  precio: number
  unidad: string
  tipo_precio: string
  fecha: string
  created_at: string
}
