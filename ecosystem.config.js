module.exports = {
  apps: [
    {
      name: 'nexum-core',
      script: 'main.py',
      interpreter: 'python3',
      watch: false,
      max_memory_restart: '800M',
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: 'storage/logs/err.log',
      out_file: 'storage/logs/out.log',
      merge_logs: true
    },
    {
      name: 'nexum-api',
      script: 'webapp/api_server.py',
      interpreter: 'python3',
      watch: false,
      max_memory_restart: '400M',
      env: {
        PORT: '8080',
        PYTHONUNBUFFERED: '1'
      },
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: 'storage/logs/api_err.log',
      out_file: 'storage/logs/api_out.log'
    },
    {
      name: 'nexum-sentinel',
      script: 'agents/nexum_sentinel.py',
      interpreter: 'python3',
      watch: false,
      env: {
        PYTHONUNBUFFERED: '1'
      },
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: 'storage/logs/sentinel.log',
      out_file: 'storage/logs/sentinel.log'
    }
  ]
};
