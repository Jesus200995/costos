import api from './api'
import type { LoginPayload, RegisterPayload, AuthResponse } from '@/types'

export const authService = {
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', payload)
    return data
  },

  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/register', {
      name: payload.name,
      email: payload.email,
      password: payload.password
    })
    return data
  },

  async getProfile(): Promise<AuthResponse['user']> {
    const { data } = await api.get<AuthResponse['user']>('/auth/profile')
    return data
  }
}
