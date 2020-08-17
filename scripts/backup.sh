#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit

filename="./backups/backup-$(date +'%Y%m%d-%H%M%S').sql.gz"

ssh sl@slasyz.ru 'pg_dump -h localhost -U toxicuser -d toxicdb | gzip' > "$filename"

du -sh ./backups/*
