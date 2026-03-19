#!/bin/bash
# deploy.sh - Script de despliegue automático para COSTOS
set -e

APP_DIR="/var/www/costos"

echo "📦 Pulling latest changes..."
cd "$APP_DIR"
git pull origin main

echo "📦 Installing backend dependencies..."
cd "$APP_DIR/backend"
npm install --production

echo "📦 Installing frontend dependencies..."
cd "$APP_DIR/pwacostos"
npm install

echo "🔨 Building frontend..."
npm run build

echo "🔄 Restarting backend..."
pm2 restart costos-backend || pm2 start "$APP_DIR/ecosystem.config.cjs"
pm2 save

echo "✅ Deploy complete!"
