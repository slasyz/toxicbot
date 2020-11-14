# TODO: check platform amd run virtualenv accordingly


DISABLE_STRICT=no-self-use,missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long,global-statement,too-few-public-methods,broad-except,redefined-builtin,protected-access,too-many-arguments,too-many-locals,fixme
DISABLE_NON_STRICT=$(DISABLE_STRICT),invalid-name,unused-argument

BACKUP_FILENAME := ./backups/backup-$(shell date +'%Y%m%d-%H%M%S').sql.gz


.PHONY: _pylint
_pylint:
	# TODO: run Linux version of pylint here
	cd ..; ./ToxicTgBot/venv/Scripts/pylint.exe ./ToxicTgBot --ignore=venv --disable="$(DISABLE)" --extension-pkg-whitelist=psycopg2._psycopg


.PHONY: pylint
pylint: DISABLE=$(DISABLE_NON_STRICT)
pylint: _pylint


.PHONY: pylint.all
pylint.all: DISABLE=$(DISABLE_STRICT)
pylint.all: _pylint


.PHONY: pytest
pytest:
	./venv/Scripts/python.exe -m pytest


.PHONY: backup
backup:
	ssh sl@slasyz.ru 'pg_dump -h localhost -U toxicuser -d toxicdb | gzip' > "$(BACKUP_FILENAME)"
	du -sh ./backups/*


.PHONY: port
port:
	echo "http://localhost:13377/messages"
	ssh -L 13377:localhost:13377 sl@slasyz.ru "sleep infinity"
