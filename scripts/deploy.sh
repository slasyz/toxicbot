#!/bin/bash

cd "$(dirname "$0")"/.. || exit 1

if [ $# -eq 0 ]
then
    echo "Usage: $0 user@hostname.ru"
    exit 1;
fi

SRC="./"
DEST="$1:~/deployments/ToxicTgBot/"

rsync -avz --progress --delete \
  --exclude='/.git' --exclude='/venv' --filter="dir-merge,- .gitignore" \
  "$SRC" "$DEST"

ssh "$1" "systemctl --user restart toxic"
