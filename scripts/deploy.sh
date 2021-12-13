#!/bin/bash

set -e

cd "$(dirname "$0")"/.. || exit 1

if [ $# -eq 0 ]
then
    echo "Usage: $0 user@hostname.ru"
    exit 1;
fi

SRC="./"
DEST="$1:~/deployments/ToxicTgBot/"

echo "-> Copying files"

rsync -avz --delete \
  --exclude='/.git' --exclude='/venv' --filter="dir-merge,- .gitignore" \
  "$SRC" "$DEST"
scp "$SRC/config.json" "$1:/etc/toxic/config.json"
scp "$SRC/systemd/toxic-main.service" "$SRC/systemd/toxic-server.service" "$1:~/.config/systemd/user/"

ssh "$1" "/bin/bash ~/deployments/ToxicTgBot/scripts/install.sh"

echo "-> Deployment is done"
