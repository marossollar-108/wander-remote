module.exports = {
  apps: [
    {
      name: 'wander-relay',
      script: 'server.js',
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '256M',
      env: {
        NODE_ENV: 'production',
        PORT: 8765,
        MAX_SESSIONS: 100,
        SESSION_TIMEOUT_MS: 300000,
        RATE_LIMIT_PER_MIN: 100,
      },
    },
  ],
};
