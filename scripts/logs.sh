#!/bin/bash

set -e

if [ $# -eq 0 ]
then
    echo "Usage: $0 user@hostname.ru"
    exit 1;
fi

ssh "$1" "tail -fn 50 /home/sl/logs/ToxicTgBot/log.log"
