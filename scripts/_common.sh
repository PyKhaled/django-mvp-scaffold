#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")
cd "$PROJECT_ROOT"

if [ -f .env ]; then
    set -a
    . ./.env
    set +a
fi

PYTHON=${PYTHON:-python3.12}
export PYTHON
