##*********************
##* Makefile commands *
##*********************
##

export SHELL := /bin/bash
export PYTHON_INTERPRETER := $(shell ( ls ./venv/Scripts/python.exe ./venv/bin/python 2> /dev/null || echo python ) | head -n 1)

.DEFAULT_GOAL := help


.PHONY: help
help:           ## show this help
	@sed -nE '/@sed/!s/##\s?//p' Makefile


.PHONY: lint
lint:           ## run linter with less strict checks
lint: DISABLE=invalid-name,unused-argument,too-many-instance-attributes
lint: pylint

.PHONY: lint.all
lint.all:       ## run linter with all usable checks
lint.all: pylint


.PHONY: pylint
pylint:         ## run pylint (with disabled checks specified in $DISABLE variable)
	$(PYTHON_INTERPRETER) -m pylint ./main.py ./toxic --rcfile="./pylintrc" --disable="$(DISABLE)"


.PHONY: test.unit
test.unit:      ## run unit tests
	$(PYTHON_INTERPRETER) -m pytest tests/unit

.PHONY: test
test:           ## run all tests (you can start dependencies using ./scripts/start-deps.sh)
	$(PYTHON_INTERPRETER) -m pytest tests


.PHONY: deps
deps:           ## install all dependencies from requirements.txt to virtual environment
	if [[ ! -d venv ]]; then \
		virtualenv venv -p python3.9; \
	fi;
	./venv/bin/python -m pip install -r requirements.txt


.PHONY: deps.global
deps.global:    ## install all dependencies from requirements.txt globally
	pip install -r requirements.txt

.PHONY: run
run:            ## start bot in foreground
	$(PYTHON_INTERPRETER) ./main.py
