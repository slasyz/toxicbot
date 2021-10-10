#!/bin/bash

if [ $# -eq 0 ]
then
    echo "Usage: $0 user@hostname.ru"
    exit 1;
fi

echo "http://localhost:8000/messages"
echo "$ pgcli -h localhost -p 5432 -U toxic -d toxic"
ssh -L 5432:localhost:5432 -L 8000:localhost:8000 "$1" "sleep infinity"
