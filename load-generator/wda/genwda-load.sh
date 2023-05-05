#!/bin/bash

START_USER=1000
LOAD_FILE_NUM=0
CONTAINER_NUM=0
DEBUG=1
DURATION=300
TOKEN_EXPIRATION=600
TTL=30
EXT="@wazo.io"

for x in $(seq 1 10);do 
    HOST_NUM=0
    LOAD_FILE_NUM=$((LOAD_FILE_NUM + 1))
    LOAD_FILE=wda$LOAD_FILE_NUM.yml

cat >$LOAD_FILE <<EOF
loads:
  - load:
EOF

for x in $(seq 1 10); do
    HOST_NUM=$(( HOST_NUM + 1 ))
    HOST=trafgen$HOST_NUM.load.wazo.io

    for y in $(seq 1 30); do
        CONTAINER_NUM=$(( CONTAINER_NUM + 1 ))
        START_USER=$(( START_USER + 1 ))
        TIMER=$((1 + RANDOM % 60))
cat >>$LOAD_FILE <<EOF
    - node:
      host: $HOST
      container: wda-load-test$CONTAINER_NUM
      cmd: "sleep $TIMER && node /usr/src/app/index.js"
      env:
        LOGIN: $START_USER$EXT
        PASSWORD: superpass
        SERVER: wazo-5000-1.load.wazo.io
        SESSION_DURATION: $DURATION
        DEBUG: $DEBUG
        TOKEN_EXPIRATION: $TOKEN_EXPIRATION
EOF
    done
    CONTAINER_NUM=0

done
cat >>$LOAD_FILE <<EOF
    ttl: $TTL
    tag: wda-load
    compose: /etc/trafgen/Docker-compose.yml
    forever: True
EOF
done

scp wda*.yml grafana:/root/
