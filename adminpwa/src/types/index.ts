export interface AdminUser {
  id: number
  nombre: string
  apellido_paterno: string
  apellido_materno: string
  curp: string
  correo: string
  telefono: string
  rol: 'usuario' | 'administrador'
  estatus: 'activo' | 'inactivo'
  created_at: string
}

export interface PWAUser {
  id: string
  name: string
  email: string
  curp: string | null
  tipo_capturista: string | null
  estado: string | null
  municipio: number | null
  localidad: string | null
  telefono: string | null
  cac_id: string | null
  cac_nombre: string | null
  territorio: string | null
  ruta: string | null
  rol_comision: string | null
  correo_institucional: string | null
  rol_interno: string | null
  created_at: string
}

export interface LoginPayload {
  correo: string
  password: string
}

export interface RegisterPayload {
  nombre: string
  apellido_paterno: string
  apellido_materno: string
  curp: string
  correo: string
  telefono: string
  password: string
  rol: 'usuario' | 'administrador'
}

export interface AuthResponse {
  user: AdminUser
  token: string
}
