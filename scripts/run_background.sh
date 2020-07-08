#!/usr/bin/env bash

cd "$(dirname "$0")" || exit

tmux new-session -s ToxicTgBot -d \"./run.sh\"
