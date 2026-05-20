module.exports = {
  apps: [
    {
      name: "nexum-core",
      script: "./main.py",
      interpreter: "python3",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        PYTHONPATH: ".",
        PYTHONUNBUFFERED: "1"
      },
      error_file: "./storage/logs/err.log",
      out_file: "./storage/logs/out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      restart_delay: 5000
    }
  ]
};
