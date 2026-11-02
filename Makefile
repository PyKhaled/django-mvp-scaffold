PYTHON ?= python3.12
INIT_ARGS ?=
HOST ?= 127.0.0.1
PORT ?= 8000

.PHONY: init config-check build test start debug

init:
	$(PYTHON) tools/init_project.py $(INIT_ARGS)

config-check:
	PYTHON="$(PYTHON)" ./scripts/build.sh --check-only

build:
	PYTHON="$(PYTHON)" ./scripts/build.sh

test:
	PYTHON="$(PYTHON)" ./scripts/test.sh

start:
	PYTHON="$(PYTHON)" HOST="$(HOST)" PORT="$(PORT)" ./scripts/start.sh

debug:
	PYTHON="$(PYTHON)" HOST="$(HOST)" PORT="$(PORT)" ./scripts/debug.sh
