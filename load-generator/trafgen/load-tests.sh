#!/bin/bash

BIN_DIR="/trafgen/xivo-load-tester"
BIN="$BIN_DIR/load-tester"
LOG_DIR="/trafgen/logs"
COMMAND="$BIN -d $LOG_DIR"

# CONFIG_LOAD REMOTE_HOST SOURCE_IP come from the trafgen.env file
# which is sourced when Docker-compose runs the container.
if [ "$CONFIG_LOAD" == "true" ]; then
    cp /trafgen/config.py /trafgen/xivo-load-tester/etc/conf.py
    sed -i "s/skaro-load/$REMOTE_HOST/"g /trafgen/xivo-load-tester/etc/conf.py
    sed -i "s/192.168.32.241/$SOURCE_IP/"g /trafgen/xivo-load-tester/etc/conf.py
fi

# SCENARIO variable come from the trafgen.env file which is sourced by
# the docker exec command.
$COMMAND $BIN_DIR/scenarios/$SCENARIO
