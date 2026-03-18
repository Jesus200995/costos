export interface User {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt: string
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
