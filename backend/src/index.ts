import express from 'express'
import cors from 'cors'
import { env } from './config/env.js'
import authRoutes from './routes/auth.routes.js'

const app = express()

app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:4173', 'https://costos.sembrandodatos.com'],
  credentials: true
}))

app.use(express.json({ limit: '1mb' }))

// Routes
app.use('/api/auth', authRoutes)

// Health check
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

app.listen(env.PORT, () => {
  console.log(`🚀 Backend corriendo en http://localhost:${env.PORT}`)
})
