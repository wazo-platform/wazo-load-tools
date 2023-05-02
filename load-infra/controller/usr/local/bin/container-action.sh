#!/bin/bash


if [ $# -ne 3 ]; then
    echo missing arguments
    echo USAGE  : container-action.sh NODE CONTAINER ACTION
    echo Example: container-action.sh trafgen1.load.wazo.io caller start
    echo Example: container-action.sh trafgen1.load.wazo.io caller stop
    echo Example: container-action.sh trafgen1.load.wazo.io caller restart
    exit 1
fi

NODE=$1
CONTAINER=$2
ACTION=$3

ssh -f root@$NODE "sh -c 'nohup docker-compose $ACTION $CONTAINER > /dev/null 2>&1 &'"
