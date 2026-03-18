export interface UserRow {
  id: string
  name: string
  email: string
  password: string
  avatar: string | null
  created_at: string
}

export interface UserPublic {
  id: string
  name: string
  email: string
  avatar?: string
  createdAt: string
}

export interface JwtPayload {
  userId: string
}
