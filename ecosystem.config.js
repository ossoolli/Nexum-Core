module.exports = {
  apps: [
    {
      name: "nexum-core",
      script: "main.py",
      interpreter: "python", // On Windows, PM2 uses global python. Make sure you activate venv if needed before running pm2 start.
      cwd: "c:\\Users\\Administrator\\Downloads\\Mutaz-dev-master\\Nexum-Core",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    },
    {
      name: "nexum-runtime-api",
      script: "webapp/api_server.py",
      interpreter: "python",
      cwd: "c:\\Users\\Administrator\\Downloads\\Mutaz-dev-master\\Nexum-Core",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
}
