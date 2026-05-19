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
    },
    {
      name: "nexum-chronos",
      script: "agents/chronos.py",
      interpreter: "./venv/bin/python",
      cwd: "/home/madarmutaz/Mutaz-dev",
      autorestart: true,
      watch: false,
      max_memory_restart: "256M",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    },
    {
      name: "nexum-bot-fleet",
      script: "core/bot_fleet.py",
      interpreter: "./venv/bin/python",
      cwd: "/home/madarmutaz/Mutaz-dev",
      autorestart: true,
      watch: false,
      max_memory_restart: "200M",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    },
    {
      name: "nexum-channel-manager",
      script: "agents/channel_manager.py",
      interpreter: "./venv/bin/python",
      cwd: "/home/madarmutaz/Mutaz-dev",
      autorestart: true,
      cron_restart: "0 * * * *",
      watch: false,
      max_memory_restart: "200M",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
}
