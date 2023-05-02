#!/bin/bash

run () {
    local node=$1
    local action=$2 
    if [ "$action" == "reload" ];then
        ssh -f root@$node "sh -c 'nohup systemctl daemon-reload > /dev/null 2>&1 &'"
    else
        ssh -f root@$node "sh -c 'nohup systemctl $action load-test.service > /dev/null 2>&1 &'"
    fi
}

if [ $# -ne 2 ]; then
    echo 'usage:    ./action NODE ACTION'
    echo "ACTION: start, stop, restart, reload"
    echo "reload is equivalent to systemctl daemon-reload"
    echo examples:
    echo "--- start a specific node                       :        ./action trafgen1.load.wazo.io start"
    echo "--- stop a specific node                       :         ./action trafgen1.load.wazo.io stop"
    echo "--- reload daemon after unit file changes      :         ./action trafgen1.load.wazo.io reload"
    echo "--- restart all nodes                          :         ./action all restart"
    exit 1
fi

action=$2
case "$1" in
    "all")
        NODES=$(cat /etc/trafgen/nodes)
        for NODE in $(echo $NODES); do
            run $NODE $2
        done
        ;;
    *)
        run $1 $2
        ;;
esac
