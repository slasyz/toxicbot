#!/usr/bin/env bash

echo "http://localhost:13377/messages"
ssh -L 13377:localhost:13377 sl@slasyz.ru "sleep infinity"
