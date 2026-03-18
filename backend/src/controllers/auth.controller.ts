import { Request, Response } from 'express'
import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'
import { randomUUID } from 'crypto'
import db from '../config/database.js'
import { env } from '../config/env.js'
import type { UserRow, UserPublic } from '../types/index.js'

function toPublicUser(row: UserRow): UserPublic {
  return {
    id: row.id,
    name: row.name,
    email: row.email,
    avatar: row.avatar || undefined,
    createdAt: row.created_at
  }
}

function generateToken(userId: string): string {
  return jwt.sign({ userId }, env.JWT_SECRET, { expiresIn: '7d' })
}

export async function register(req: Request, res: Response): Promise<void> {
  try {
    const { name, email, password } = req.body

    if (!name || !email || !password) {
      res.status(400).json({ message: 'Todos los campos son obligatorios' })
      return
    }

    if (typeof name !== 'string' || name.trim().length < 2) {
      res.status(400).json({ message: 'El nombre debe tener al menos 2 caracteres' })
      return
    }

    if (typeof email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      res.status(400).json({ message: 'Correo electrónico inválido' })
      return
    }

    if (typeof password !== 'string' || password.length < 6) {
      res.status(400).json({ message: 'La contraseña debe tener al menos 6 caracteres' })
      return
    }

    const existing = db.prepare('SELECT id FROM users WHERE email = ?').get(email)
    if (existing) {
      res.status(409).json({ message: 'Este correo ya está registrado' })
      return
    }

    const id = randomUUID()
    const hashedPassword = await bcrypt.hash(password, 12)
    const now = new Date().toISOString()

    db.prepare(
      'INSERT INTO users (id, name, email, password, created_at) VALUES (?, ?, ?, ?, ?)'
    ).run(id, name.trim(), email.toLowerCase().trim(), hashedPassword, now)

    const user: UserRow = {
      id,
      name: name.trim(),
      email: email.toLowerCase().trim(),
      password: hashedPassword,
      avatar: null,
      created_at: now
    }

    const token = generateToken(id)

    res.status(201).json({
      user: toPublicUser(user),
      token
    })
  } catch (error) {
    console.error('Register error:', error)
    res.status(500).json({ message: 'Error interno del servidor' })
  }
}

export async function login(req: Request, res: Response): Promise<void> {
  try {
    const { email, password } = req.body

    if (!email || !password) {
      res.status(400).json({ message: 'Correo y contraseña son obligatorios' })
      return
    }

    const user = db.prepare('SELECT * FROM users WHERE email = ?').get(
      (email as string).toLowerCase().trim()
    ) as UserRow | undefined

    if (!user) {
      res.status(401).json({ message: 'Credenciales incorrectas' })
      return
    }

    const valid = await bcrypt.compare(password, user.password)
    if (!valid) {
      res.status(401).json({ message: 'Credenciales incorrectas' })
      return
    }

    const token = generateToken(user.id)

    res.json({
      user: toPublicUser(user),
      token
    })
  } catch (error) {
    console.error('Login error:', error)
    res.status(500).json({ message: 'Error interno del servidor' })
  }
}

export function getProfile(req: Request, res: Response): void {
  try {
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(req.userId) as UserRow | undefined

    if (!user) {
      res.status(404).json({ message: 'Usuario no encontrado' })
      return
    }

    res.json(toPublicUser(user))
  } catch (error) {
    console.error('Profile error:', error)
    res.status(500).json({ message: 'Error interno del servidor' })
  }
}
