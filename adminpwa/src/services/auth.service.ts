import api from './api'
import type { LoginPayload, RegisterPayload, AuthResponse, AdminUser } from '@/types'

export const authService = {
  async login(data: LoginPayload): Promise<AuthResponse> {
    const res = await api.post('/admin/login', data)
    return res.data
  },

  async register(data: RegisterPayload): Promise<AuthResponse> {
    const res = await api.post('/admin/register', data)
    return res.data
  },

  async getMe(token: string): Promise<AdminUser> {
    const res = await api.get('/admin/me', { params: { token } })
    return res.data
  },

  async getUsuarios(token: string): Promise<AdminUser[]> {
    const res = await api.get('/admin/usuarios', { params: { token } })
    return res.data
  },

  async updateEstatus(userId: number, estatus: string, token: string): Promise<AdminUser> {
    const res = await api.patch(`/admin/usuarios/${userId}/estatus`, { estatus }, { params: { token } })
    return res.data
  },

  async updateRol(userId: number, rol: string, token: string): Promise<AdminUser> {
    const res = await api.patch(`/admin/usuarios/${userId}/rol`, { rol }, { params: { token } })
    return res.data
  },

  async deleteUsuario(userId: number, token: string): Promise<void> {
    await api.delete(`/admin/usuarios/${userId}`, { params: { token } })
  }
}
