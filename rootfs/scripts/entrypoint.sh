#!/bin/bash
set -e
CONFIG=${CONFIG:-/config/daydusk.yml}

if [ "$1" = 'daydusk' ]; then
  
  # Generate crontab if it doesn't exist
  if [ ! -f /config/daydusk.crontab ]; then

    if [ -f "${CONFIG}" ]; then
      LIFX_CONFIG=${CONFIG} /usr/local/bin/python /scripts/generate-crontab.py 
      cat /config/daydusk.crontab
    else
      echo "Config file not found."
      exit 1
    fi
  
  fi

  exec /usr/local/bin/supercronic /config/daydusk.crontab
fi

exec "$@"