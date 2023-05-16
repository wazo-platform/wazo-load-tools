#!/bin/bash

START_USER=1000
LOAD_FILE_NUM=0
CONTAINER_NUM=0
CONTAINER_TRACK=0
DEBUG=1
DISABLE_CHATD=1
DURATION=300
TOKEN_EXPIRATION=600
DELAY_CNX_RAND=60
TTL=30
EXT="@wazo.io"
#SERVER=router-1.load.wazo.io
SERVER=wazo-5000-1.load.wazo.io

LOAD_FILES_NUMBER=1
for x in $(seq 1 $LOAD_FILES_NUMBER);do # number of  load files
    LOAD_FILE_NUM=$((LOAD_FILE_NUM + 1))
    LOAD_FILE=wda$LOAD_FILE_NUM.yml

cat >$LOAD_FILE <<EOF
loads:
EOF
    LOAD_SECTIONS=5
    for x in $(seq 1 $LOAD_SECTIONS); do  # number of load sections in the load file
        HOST_NUM=0
    echo LOAD SECTION
cat >>$LOAD_FILE <<EOF
  - load:
EOF

        TRAFGEN_NUMBER=10
        for x in $(seq 1 $TRAFGEN_NUMBER); do  # trafgen number
            HOST_NUM=$(( HOST_NUM + 1 ))
            HOST=trafgen$HOST_NUM.load.wazo.io
            CONTAINER_NUM=$CONTAINER_TRACK

            CLIENTS=20
            for y in $(seq 1 $CLIENTS); do  # number of clients
                CONTAINER_NUM=$(( CONTAINER_NUM + 1 ))
                START_USER=$(( START_USER + 1 ))
                TIMER=$((1 + RANDOM % $DELAY_CNX_RAND))
cat >>$LOAD_FILE <<EOF
    - node:
      host: $HOST
      container: wda-load-test$CONTAINER_NUM
      cmd: "sleep $TIMER && node /usr/src/app/index.js"
      env:
        LOGIN: $START_USER$EXT
        PASSWORD: superpass
        SERVER: $SERVER
        SESSION_DURATION: $DURATION
        DEBUG: $DEBUG
        TOKEN_EXPIRATION: $TOKEN_EXPIRATION
        DISABLE_CHATD: $DISABLE_CHATD
EOF
            done

        done
cat >>$LOAD_FILE <<EOF
    ttl: $TTL
    tag: wda-load
    compose: /etc/trafgen/Docker-compose.yml
    forever: True
EOF
        CONTAINER_TRACK=$(( $CONTAINER_TRACK + $CLIENTS ))
    done

done

scp wda*.yml grafana:/root/load/without-router
