module.exports = {
  apps: [
    {
      name: "nexum-core",
      script: "main.py",
      interpreter: "./venv/bin/python",
      cwd: "/home/madarmutaz/Mutaz-dev",
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
      interpreter: "./venv/bin/python",
      cwd: "/home/madarmutaz/Mutaz-dev",
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
}
