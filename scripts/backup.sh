#!/bin/bash

cd "$(dirname "$0")"/.. || exit 1

if [ $# -eq 0 ]
then
    echo "Usage: $0 user@hostname.ru"
    exit 1;
fi

BACKUP_FILENAME=./backups/backup-$(date +'%Y%m%d-%H%M%S')

ssh "$1" 'pg_dump --data-only --inserts -h localhost -U toxic -d toxic | gzip' > "$BACKUP_FILENAME-host.sql.gz"
du -sh ./backups/*
