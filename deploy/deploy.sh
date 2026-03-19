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

# Copiar .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Archivo .env creado desde .env.example - Revisa la configuración"
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
cd "$APP_DIR"
pm2 startOrRestart deploy/ecosystem.config.cjs --update-env

# Guardar config PM2
pm2 save

echo "✅ Despliegue completado exitosamente!"
echo "🌐 https://costos.sembrandodatos.com"
