#!/bin/bash

set -e

cd "$(dirname "$0")"/.. || exit 1

echo "-> Replacing variables"

FILES_WITH_VARS="/home/sl/.config/systemd/user/toxic-main.service /home/sl/.config/systemd/user/toxic-server.service"
export PROJECT_DIR=$(pwd)
export PROJECT_LOG_DIR="/home/sl/logs/ToxicTgBot"

for file in $FILES_WITH_VARS; do
  tmp=$(mktemp)
  envsubst < "$file" > "$tmp";
  mv "$tmp" "$file";
done;

echo "-> Syncing deps"

make deps

echo "-> Reloading everything"

systemctl --user daemon-reload
systemctl --user restart toxic-main
systemctl --user restart toxic-server
# Add this line to sudoers file to reload Caddy without password:
#  %sudo ALL=NOPASSWD: /bin/systemctl reload caddy
sudo systemctl reload caddy

echo "-> Installation is done."
