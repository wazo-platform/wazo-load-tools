#!/bin/bash

BIN_DIR="/trafgen/xivo-load-tester"
BIN="$BIN_DIR/load-tester"
LOG_DIR="/trafgen/logs"
COMMAND="$BIN -d $LOG_DIR"

# CONFIG_LOAD REMOTE_HOST SOURCE_IP come from the trafgen.env file
# which is sourced by the docker exec command to export these variables
# to the script environment.
if [ "$CONFIG_LOAD" == "true" ]; then
    cp /trafgen/xivo-load-tester/etc/conf.py.sample /trafgen/xivo-load-tester/etc/conf.py
    sed -i "s/skaro-load/$REMOTE_HOST/"g /trafgen/xivo-load-tester/etc/conf.py
    sed -i "s/192.168.32.241/$SOURCE_IP/"g /trafgen/xivo-load-tester/etc/conf.py
fi

# LOAD_TEST variable come from the trafgen.env file which is sourced by 
# the docker exec command.
case $LOAD_TEST in
    "answer-then-hangup")
        $COMMAND $BIN_DIR/scenarios/answer-then-hangup
        ;;
    "answer-then-wait")
        $COMMAND $BIN_DIR/scenarios/answer-then-wait
        ;;
    "call-then-cancel-on-ringing")
        $COMMAND $BIN_DIR/scenarios/call-then-cancel-on-ringing
        ;;
    "call-then-hangup")
        $COMMAND $BIN_DIR/scenarios/call-then-hangup
        ;;
    "call-the-wait-decline")
        $COMMAND $BIN_DIR/scenarios/call-the-wait-decline
        ;;
    "call-then-wait-tel")
        $COMMAND $BIN_DIR/scenarios/call-then-wait-tel
        ;;
    "call-then-wait")
        $COMMAND $BIN_DIR/scenarios/call-then-wait
        ;;
    "ring-then-wait-cancel")
        $COMMAND $BIN_DIR/scenarios/ring-then-wait-cancel
        ;;
    "send-sip-register")
        $COMMAND $BIN_DIR/scenarios/send-sip-register
        ;;
    "all")
        $COMMAND $BIN_DIR/scenarios/answer-then-hangup
        $COMMAND $BIN_DIR/scenarios/answer-then-wait
        $COMMAND $BIN_DIR/scenarios/call-then-cancel-on-ringing
        $COMMAND $BIN_DIR/scenarios/call-then-hangup
        $COMMAND $BIN_DIR/scenarios/call-the-wait-decline
        $COMMAND $BIN_DIR/scenarios/call-then-wait-tel
        $COMMAND $BIN_DIR/scenarios/call-then-wait
        $COMMAND $BIN_DIR/scenarios/ring-then-wait-cancel
        $COMMAND $BIN_DIR/scenarios/send-sip-register
        ;;

esac
