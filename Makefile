## *********************
## * Makefile commands *
## *********************
##


PYTHON_INTERPRETER=$(shell ls ./venv/Scripts/python.exe ./venv/bin/python 2> /dev/null)

BACKUP_FILENAME := ./backups/backup-$(shell date +'%Y%m%d-%H%M%S').sql.gz


.DEFAULT_GOAL := help


.PHONY: backup
backup:       ## create remote database backup in local directory
	ssh sl@slasyz.ru 'pg_dump -h localhost -U toxicuser -d toxicdb | gzip' > "$(BACKUP_FILENAME)"
	du -sh ./backups/*


.PHONY: deps
deps:         ## install all dependencies from requirements.txt
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt


.PHONY: help
help:         ## show this help
	@sed -ne '/@sed/!s/##\s\?//p' $(MAKEFILE_LIST)


.PHONY: init
init:         ## create virtual environment
	virtualenv venv -p python3
	$(MAKE) deps


.PHONY: lint
lint:         ## run linter with less strict checks
lint: DISABLE=invalid-name,unused-argument
lint: pylint


.PHONY: lint.all
lint.all:     ## run linter with all usable checks
lint.all: pylint


.PHONY: port
port:         ## run port forwarding to open Flask server locally
	echo "http://localhost:13377/messages"
	ssh -L 13377:localhost:13377 sl@slasyz.ru "sleep infinity"


.PHONY: pylint
pylint:       ## run pylint (with disabled checks specified in $DISABLE variable)
	cd ..; ./ToxicTgBot/$(PYTHON_INTERPRETER) -m pylint ./ToxicTgBot --rcfile="./ToxicTgBot/pylintrc" --disable="$(DISABLE)"


.PHONY: run
run:          ## start bot in foreground
	$(PYTHON_INTERPRETER) ./main.py


.PHONY: test
test:         ## run unit tests
	$(PYTHON_INTERPRETER) -m pytest tests/unit


.PHONY: test.all
test.all:     ## run all tests
	$(PYTHON_INTERPRETER) -m pytest tests


.PHONY: tmux.restart
tmux.restart: ## restart tmux session
tmux.restart:
	$(MAKE) tmux.stop
	sleep 2
	$(MAKE) tmux.start


.PHONY: tmux.start
tmux.start:   ## start tmux session
	tmux new-session -s ToxicTgBot -d "make run"


.PHONY: tmux.stop
tmux.stop:    ## stop tmux session
	( \
		tmux send-keys -t ToxicTgBot C-c; \
		tmux send-keys -t ToxicTgBot C-c \
	) || true
