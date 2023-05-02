#!/bin/bash

REGISTRY=registry.load.wazo.io
PORT=5000

docker pull $REGISTRY:$PORT/$1
docker tag  $REGISTRY:$PORT/$1 $1
