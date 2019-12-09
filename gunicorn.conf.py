workers=4
bind="127.0.0.1:5050"
timeout=120
worker_class="gevent"
accesslog="/var/log/gun/access.log"
errorlog="/var/log/gun/error.log"
daemon=True
