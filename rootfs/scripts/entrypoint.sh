#!/bin/bash
set -e
CONFIG=${CONFIG:-/config/daydusk.yml}

if [ "$1" = 'daydusk' ]; then
  if [ -f "${CONFIG}" ]; then
    rm -f /config/daydusk.crontab
    LIFX_CONFIG=${CONFIG} /usr/local/bin/python /scripts/generate-crontab.py
    cat /config/daydusk.crontab
  else
    echo "Config file not found."
    exit 1
  fi
  exec /usr/local/bin/supercronic -quiet -passthrough-logs /config/daydusk.crontab
fi

exec "$@"