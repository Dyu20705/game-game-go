#!/bin/sh
set -eu

case "${1:-smoke}" in
  smoke)
    exec python -m tools.smoke_test
    ;;
  test)
    exec python -m pytest -q -p no:cacheprovider
    ;;
  demo)
    exec supervisord -c /app/docker/supervisord.conf
    ;;
  *)
    exec "$@"
    ;;
esac
