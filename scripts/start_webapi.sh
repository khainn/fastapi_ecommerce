#! /bin/bash
set -e
worker=${WORKER:-1}

alembic upgrade head
gunicorn --bind 0.0.0.0:8000 -k gevent -w ${worker} --timeout 1800 project.wsgi
