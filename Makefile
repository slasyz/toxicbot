# TODO: check platform amd run virtualenv accordingly


  ## *********************
  ## * Makefile commands *
  ## *********************
  ##


DISABLE_STRICT=no-self-use,missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long,global-statement,too-few-public-methods,broad-except,redefined-builtin,protected-access,too-many-arguments,too-many-locals,fixme
DISABLE_NON_STRICT=$(DISABLE_STRICT),invalid-name,unused-argument

BACKUP_FILENAME := ./backups/backup-$(shell date +'%Y%m%d-%H%M%S').sql.gz


.PHONY: backup
backup:       ## create remote database backup in local directory
	ssh sl@slasyz.ru 'pg_dump -h localhost -U toxicuser -d toxicdb | gzip' > "$(BACKUP_FILENAME)"
	du -sh ./backups/*


.PHONY: help
help:         ## show this help
	@sed -ne '/@sed/!s/  ##\s\?//p' $(MAKEFILE_LIST)


.PHONY: lint
lint:         ## run linter with less strict checks
lint: DISABLE=$(DISABLE_NON_STRICT)
lint: pylint


.PHONY: lint.all
lint.all:     ## run linter with all usable checks
lint.all: DISABLE=$(DISABLE_STRICT)
lint.all: pylint


.PHONY: port
port:         ## run port forwarding to open Flask server locally
	echo "http://localhost:13377/messages"
	ssh -L 13377:localhost:13377 sl@slasyz.ru "sleep infinity"


.PHONY: pylint
pylint:       ## run pylint (with disabled checks specified in $DISABLE variable)
	# TODO: run Linux version of pylint here
	cd ..; ./ToxicTgBot/venv/Scripts/pylint.exe ./ToxicTgBot --ignore=venv --disable="$(DISABLE)" --extension-pkg-whitelist=psycopg2._psycopg


.PHONY: run
run:          ## start bot in foreground
	./venv/bin/python3 ./main.py


.PHONY: test
test:         ## run unit tests
	./venv/Scripts/python.exe -m pytest


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
		tmux send-keys -t ToxicTgBot C-c \
		tmux send-keys -t ToxicTgBot C-c \
    ) || true
