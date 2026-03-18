import { Request, Response, NextFunction } from 'express'
import jwt from 'jsonwebtoken'
import { env } from '../config/env.js'
import type { JwtPayload } from '../types/index.js'

declare global {
  namespace Express {
    interface Request {
      userId?: string
    }
  }
}

export function authMiddleware(req: Request, res: Response, next: NextFunction): void {
  const header = req.headers.authorization
  if (!header?.startsWith('Bearer ')) {
    res.status(401).json({ message: 'Token no proporcionado' })
    return
  }

  const token = header.slice(7)

  try {
    const decoded = jwt.verify(token, env.JWT_SECRET) as JwtPayload
    req.userId = decoded.userId
    next()
  } catch {
    res.status(401).json({ message: 'Token inválido o expirado' })
  }
}
