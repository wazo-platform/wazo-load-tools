#!/bin/bash

if [ $# -ne 2 ]; then
    echo missing arguments
    echo USAGE  : stop-load.sh NODE CONTAINER
    echo Example: stop-load.sh trafgen1.load.wazo.io caller

    exit 1
fi

NODE=$1
CONTAINER=$2

container-action.sh $NODE $CONTAINER restart
