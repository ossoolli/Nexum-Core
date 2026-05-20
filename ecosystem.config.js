module.exports = {
  apps: [
    {
      name: "nexum-core",
      script: "python",
      args: "main.py",
      interpreter: "python",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "production",
        PYTHONUNBUFFERED: "1"
      },
      error_file: "storage/logs/err.log",
      out_file: "storage/logs/out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      restart_delay: 5000
    }
  ]
};
