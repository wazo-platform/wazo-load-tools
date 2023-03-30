#!/bin/bash -x

USER=$1
PASSWORD=$2
STACK=${3-172.16.43.10}

curl -X POST -u $USER:$PASSWORD --header 'Content-Type: application/json' \
    --header 'Accept: application/json' \
    -d '{ "expiration": 860000 }' \
    'https://$STACK:443/api/auth/0.1/token'
