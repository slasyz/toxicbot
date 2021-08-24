#!/bin/bash

MAX_WAITING_TIMEOUT_SECONDS=60

set -e

docker-compose up -d --build --force-recreate

for _ in $(seq $MAX_WAITING_TIMEOUT_SECONDS); do
  echo -n "."

  if [[ $(docker ps -q -f "health=unhealthy") ]]; then
    echo
    echo "***************************************"
    echo "* ERROR: found an unhealthy container *"
    echo "***************************************"
    docker ps
    exit 1
  fi

  if [[ ( -z $(docker ps -q -f "health=starting") ) && ( -z $(docker ps -q -f "health=unhealthy") ) ]]; then
    echo
    echo "-> All containers have started."
    exit
  fi

  sleep 1
done

echo "******************"
echo "* ERROR: timeout *"
echo "******************"
docker ps
exit 1
