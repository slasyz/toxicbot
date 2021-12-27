#!/bin/bash

set -e

cd "$(dirname "$0")"/.. || exit 1

echo "-> Replacing variables"

FILES_WITH_VARS="/home/sl/.config/systemd/user/toxic-main.service /home/sl/.config/systemd/user/toxic-server.service"
PROJECT_DIR=$(pwd)
export PROJECT_DIR
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

echo "-> Installation is done."
