#!/bin/bash

if [ $# -lt 2 ]
then
    echo "Usage: $0 user@hostname.ru start|stop|restart"
    exit 1;
fi

ssh "$1" "systemctl --user $2 toxic"
