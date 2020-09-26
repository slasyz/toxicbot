#!/usr/bin/env bash

cd "$(dirname "$0")/../.." || exit

DISABLE=no-self-use,missing-module-docstring,missing-class-docstring,missing-function-docstring,line-too-long,global-statement,too-few-public-methods,broad-except,redefined-builtin,protected-access,too-many-arguments,too-many-locals,fixme

if [[ "$1" != "--more" ]]; then
  DISABLE="$DISABLE,invalid-name,unused-argument"
fi

./ToxicTgBot/venv/bin/pylint -j 0 ./ToxicTgBot --ignore=venv --disable="$DISABLE" --extension-pkg-whitelist=psycopg2._psycopg
