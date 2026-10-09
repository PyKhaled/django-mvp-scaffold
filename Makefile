PYTHON ?= python3.12
INIT_ARGS ?=

.PHONY: init config-check
init:
	$(PYTHON) tools/init_project.py $(INIT_ARGS)

# .env is generated with shell-safe values; Django does not load it itself.
config-check:
	@set -a; . ./.env; set +a; $(PYTHON) manage.py check
