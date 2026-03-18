import Database from 'better-sqlite3'
import { env } from './env.js'
import { mkdirSync } from 'fs'
import { dirname } from 'path'

// Ensure data directory exists
mkdirSync(dirname(env.DB_PATH), { recursive: true })

const db = new Database(env.DB_PATH)

// Enable WAL mode for better performance
db.pragma('journal_mode = WAL')
db.pragma('foreign_keys = ON')

// Create tables
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    avatar TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
  )
`)

export default db
