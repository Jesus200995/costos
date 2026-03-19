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
