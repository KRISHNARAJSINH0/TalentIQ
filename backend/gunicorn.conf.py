import multiprocessing

# Gunicorn socket binding
bind = "0.0.0.0:8000"

# Production concurrency adjustments
workers = 2
threads = 2
worker_class = "gthread"

# Request lifespans
timeout = 60
keepalive = 5

# Process naming
proc_name = "resumeai_gunicorn"

# Logging setup
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Graceful restarts
graceful_timeout = 30
max_requests = 1200
max_requests_jitter = 50
