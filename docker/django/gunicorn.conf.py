# Gunicorn configuration for production
bind = "0.0.0.0:10000"
workers = 4
worker_class = "sync"
timeout = 60
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "-"
errorlog = "-"
loglevel = "info"
daemon = False
