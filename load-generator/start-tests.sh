#!/bin/bash


if [ $# -ne 2 ]; then
	echo "Usage:   start-tests.sh CONTAINER SCENARIO"
	echo "example: ./start-tests.sh trafgen-callee answer-then-wait"
fi

CONTAINER=$1
RUNNING_STATE=false
while [ $RUNNING_STATE != "true" ]
do
	RUNNING_STATE=$(docker container inspect $CONTAINER | jq -r .[].State.Running)
done

SCENARIO=$2
exec docker exec  --env SCENARIO=$SCENARIO $CONTAINER bash -c "/trafgen/load-tests.sh"
