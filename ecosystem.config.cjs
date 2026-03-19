module.exports = {
  apps: [{
    name: 'costos-backend',
    script: 'node_modules/.bin/tsx',
    args: 'src/index.ts',
    cwd: '/var/www/costos/backend',
    env: {
      NODE_ENV: 'production',
      PORT: 3001
    },
    instances: 1,
    autorestart: true,
    max_memory_restart: '256M',
    watch: false
  }]
}
