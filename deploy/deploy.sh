#!/bin/bash
set -e

# ================================================
# COSTOS - Script de despliegue automático
# Se ejecuta cada vez que se hace git pull
# ================================================

APP_DIR="/var/www/costos"
LOG_DIR="/var/log/costos"

echo "🚀 Desplegando COSTOS..."
echo "📅 $(date)"

cd "$APP_DIR"

# Instalar dependencias del backend
echo "📦 Instalando dependencias del backend..."
cd "$APP_DIR/backend"
npm ci --production 2>/dev/null || npm install --production
npm rebuild better-sqlite3

# Copiar .env si no existe
if [ ! -f .env ]; then
    echo 'PORT=3001' > .env
    echo 'JWT_SECRET=costos_prod_secret_change_me' >> .env
    echo 'DB_PATH=./data/costos.db' >> .env
    echo "⚠️  Archivo .env creado - Revisa la configuración"
fi

# Crear directorio de data
mkdir -p data

# Instalar dependencias y construir frontend
echo "📦 Instalando dependencias del frontend..."
cd "$APP_DIR/pwacostos"
npm ci 2>/dev/null || npm install

echo "🔨 Construyendo frontend..."
npx vite build

# Reiniciar backend con PM2
echo "🔄 Reiniciando backend..."
cd "$APP_DIR/backend"
pm2 delete costos-backend 2>/dev/null || true
pm2 start node_modules/.bin/tsx --name costos-backend -- src/index.ts
pm2 save

echo "✅ Despliegue completado exitosamente!"
echo "🌐 https://costos.sembrandodatos.com"
