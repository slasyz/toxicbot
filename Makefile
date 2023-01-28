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


.PHONY: prepare
prepare:         ## prepare env using ansible
	ansible-playbook -i ../infra/inventory.yml --ask-vault-pass ansible/prepare-playbook.yml

.PHONY: deploy
deploy:         ## deploy using ansible
	ansible-playbook -i ../infra/inventory.yml --ask-vault-pass ansible/deploy-playbook.yml


.PHONY: fmt
fmt:            ## run autopep8
	find ./toxic main.py -name '*.py' -exec $(PYTHON_INTERPRETER) -m autopep8 --in-place --global-config pycodestyle '{}' \;


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
	MYPYPATH=. $(PYTHON_INTERPRETER) -m mypy --namespace-packages ./main.py || true


.PHONY: pylint
pylint:         ## run pylint (with disabled checks specified in $DISABLE variable)
	$(PYTHON_INTERPRETER) -m pylint ./main.py ./toxic --rcfile="./pylintrc" --disable="$(DISABLE)"


.PHONY: test.unit
test.unit:      ## run unit tests
	$(PYTHON_INTERPRETER) -m pytest tests/unit

.PHONY: test
test:           ## run all tests (you can start dependencies using ./scripts/start-deps.sh)
	$(PYTHON_INTERPRETER) -m pytest tests

.PHONY: test.detailed
test.detailed:  ## run all tests (you can start dependencies using ./scripts/start-deps.sh)
	$(PYTHON_INTERPRETER) -m pytest -vv tests


.PHONY: deps
deps:           ## install all dependencies from requirements.txt to virtual environment
	if [[ ! -d venv ]]; then \
		virtualenv venv -p python3.10 --download; \
	fi;
	./venv/bin/python -m pip install -r requirements.txt
	if [[ ! -f venv/lib/python3.10/site-packages/ruwordnet/static/ruwordnet.db ]]; then \
		./venv/bin/ruwordnet download; \
	fi;

.PHONY: deps.global
deps.global:    ## install all dependencies from requirements.txt globally
	pip install -r requirements.txt
	ruwordnet download


.PHONY: run
run:            ## start bot in foreground
	$(PYTHON_INTERPRETER) ./main.py


.PHONY: server
server:         ## run server
	PYTHONPATH=. $(PYTHON_INTERPRETER) ./toxic/server/server.py
