##*********************
##* Makefile commands *
##*********************
##

export SHELL := /bin/bash
export PYTHON_INTERPRETER := $(shell ( ls ./.venv/Scripts/python.exe ./.venv/bin/python 2> /dev/null || echo python ) | head -n 1)

.DEFAULT_GOAL := help


.PHONY: help
help:           ## show this help
	@sed -nE '/@sed/!s/##\s?//p' Makefile

.PHONY: fmt
fmt:            ## run autopep8
	find ./toxic main.py -name '*.py' -exec poetry run autopep8 --in-place --global-config pycodestyle '{}' \;


.PHONY: lint
lint:           ## run linter with less strict checks
lint: DISABLE=invalid-name,unused-argument,too-many-instance-attributes
lint: pylint

.PHONY: lint.all
lint.all:       ## run linter with all usable checks
lint.all:
	make pylint || true
	make mypy || true


.PHONY: mypy
mypy:           ## run mypy
mypy:
	MYPYPATH=. poetry run mypy --namespace-packages ./main.py || true


.PHONY: pylint
pylint:         ## run pylint (with disabled checks specified in $DISABLE variable)
	poetry run pylint ./main.py ./toxic --rcfile="./pylintrc" --disable="$(DISABLE)"


.PHONY: test.unit
test.unit:      ## run unit tests
	poetry run pytest tests/unit

.PHONY: test
test:           ## run all tests (you can start dependencies using ./scripts/start-deps.sh)
	poetry run pytest tests

.PHONY: test.detailed
test.detailed:  ## run all tests (you can start dependencies using ./scripts/start-deps.sh)
	poetry run pytest -vv tests


.PHONY: deps
deps:           ## install all dependencies from requirements.txt to virtual environment
	poetry install
	if [[ ! -f .venv/lib/python3.11/site-packages/ruwordnet/static/ruwordnet.db ]]; then \
		poetry run ruwordnet download; \
	fi;


.PHONY: run
run:            ## start bot in foreground
	poetry run python ./main.py


.PHONY: server
server:         ## run server
	PYTHONPATH=. poetry run python ./toxic/server/server.py
