#!/bin/sh
set -eu

if [ "${KOLLA_BOOTSTRAP+x}" = x ]; then
    exec alembic -c skyline_apiserver/db/alembic/alembic.ini upgrade head
fi

if [ ! -f /etc/skyline/skyline.yaml ]; then
    echo "Missing /etc/skyline/skyline.yaml" >&2
    exit 1
fi

set -- --output-file /etc/nginx/nginx.conf \
    --listen-address "${LISTEN_ADDRESS:-0.0.0.0:9999}"

if [ -n "${SSL_CERTFILE:-}" ] && [ -n "${SSL_KEYFILE:-}" ]; then
    set -- "$@" --ssl-certfile "$SSL_CERTFILE" --ssl-keyfile "$SSL_KEYFILE"
fi

skyline-nginx-generator "$@"
nginx -t
nginx

exec gunicorn -c /etc/skyline/gunicorn.py skyline_apiserver.main:app
