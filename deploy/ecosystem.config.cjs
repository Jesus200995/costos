module.exports = {
  apps: [
    {
      name: 'costos-backend',
      cwd: '/var/www/costos/backend',
      script: './node_modules/.bin/tsx',
      args: 'src/index.ts',
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        PORT: 3001
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      error_file: '/var/log/costos/backend-error.log',
      out_file: '/var/log/costos/backend-out.log'
    }
  ]
}
