#!/bin/bash

set -e

cd "$(dirname "$0")"/.. || exit 1

if [ $# -eq 0 ]
then
    echo "Usage: $0 user@hostname.ru"
    exit 1;
fi

ssh "$1" "systemctl --user daemon-reload
  systemctl --user stop toxic-main &&
  systemctl --user stop toxic-server"

echo "-> Done."
