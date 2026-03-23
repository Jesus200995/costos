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
}

export interface AuthResponse {
  user: AdminUser
  token: string
}
