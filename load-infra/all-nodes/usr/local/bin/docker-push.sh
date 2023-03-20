#!/bin/bash

REGISTRY=registry.load.wazo.io
PORT=5000

docker tag $1 $REGISTRY:$PORT/$1
docker push $REGISTRY:$PORT/$1
