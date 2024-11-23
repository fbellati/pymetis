#!/bin/bash
set -e
set -o errexit
set -o xtrace

# Run additional init scripts
echo "Entrypoint execution"

DIR="/docker-entrypoint.d"
if [[ -d "$DIR" ]]; then
  echo "More entrypoint.d detected ..."
  /bin/run-parts --verbose "$DIR"
fi

exec "$@"







