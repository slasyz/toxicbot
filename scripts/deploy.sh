#!/bin/bash

cd "$(dirname "$0")"/.. || exit 1

if [ $# -eq 0 ]
then
    echo "Usage: $0 user@hostname.ru"
    exit 1;
fi

SRC="./"
DEST="$1:~/deployments/ToxicTgBot/"

rsync -avz --delete \
  --exclude='/.git' --exclude='/venv' --filter="dir-merge,- .gitignore" \
  "$SRC" "$DEST"

scp config.json "$1:/etc/toxic/config.json"
ssh "$1" 'sed -i "s/\"port\": 30121,/\"port\": 5432,/" /etc/toxic/config.json'

ssh "$1" "systemctl --user restart toxic"
