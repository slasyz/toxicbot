#!/bin/bash

cd "$(dirname "$0")"/.. || exit 1

LOG_DIR=~/logs/ToxicTgBot/backup-db
mkdir -p "$LOG_DIR"

LOG_FILENAME="$LOG_DIR/backup-$(date +'%Y%m%d-%H%M%S').log"
PYTHONPATH=. ./venv/bin/python ./scripts/backup_s3.py > "$LOG_FILENAME" 2>&1
