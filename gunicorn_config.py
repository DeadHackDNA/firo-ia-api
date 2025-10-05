# Gunicorn configuration file for production deployment
# Para Render, Railway, Heroku, etc.

import os

# Bind to PORT provided by hosting service (e.g., Render, Heroku)
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Number of worker processes (adjust based on CPU cores)
# Reducido a 1 para plan gratuito de Render (512 MB RAM)
workers = 1

# Worker class (gevent es más eficiente en memoria que sync)
worker_class = "gevent"

# Conexiones concurrentes por worker (solo para gevent)
worker_connections = 1000

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
# Desactivado para reducir uso de memoria en plan gratuito
preload_app = False

# Max requests per worker before restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 50
