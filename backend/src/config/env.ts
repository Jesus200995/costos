import dotenv from 'dotenv'
dotenv.config()

export const env = {
  PORT: parseInt(process.env.PORT || '3001', 10),
  JWT_SECRET: process.env.JWT_SECRET || 'fallback_secret_change_me',
  DB_PATH: process.env.DB_PATH || './data/costos.db'
}
