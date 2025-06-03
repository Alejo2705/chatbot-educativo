"""
Configuración de Gunicorn para producción
"""

import multiprocessing
import os

# Dirección y puerto
bind = "0.0.0.0:8000"

# Número de workers (procesos)
workers = multiprocessing.cpu_count() * 2 + 1

# Tipo de worker
worker_class = "sync"

# Timeout
timeout = 120

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# Nombre del proceso
proc_name = "chatbot_educativo"

# Reinicio automático cuando cambian los archivos (solo desarrollo)
reload = os.environ.get("ENVIRONMENT") == "development"

# Preload app
preload_app = True

# StatsD (opcional, para monitoreo)
# statsd_host = "localhost:8125"
# statsd_prefix = "chatbot"