# Gunicorn configuration file for production deployment
# Para Render, Railway, Heroku, etc.

import os

# Bind to PORT provided by hosting service (e.g., Render, Heroku)
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Number of worker processes (adjust based on CPU cores)
# Formula: (2 x CPU cores) + 1
workers = 4

# Worker class (sync is good for Flask)
worker_class = "sync"

# Timeout for requests (in seconds)
# Aumentado para cold starts y carga del modelo
timeout = 300

# Keep-alive connections
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Preload app for better performance
preload_app = True

# Max requests per worker before restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50
