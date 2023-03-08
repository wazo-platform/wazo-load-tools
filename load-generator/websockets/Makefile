.PHONY: build run exec
 
DOCKERFILE ?= Dockerfile
IMAGE = wazo-ws-client
TAG = 0.0.1

build: $(DOCKERFILE)
	docker build -t $(IMAGE):$(TAG) -f $(DOCKERFILE) .

HOST_IP ?= "localhost:8000"
ACCOUNTS ?= /etc/users.csv
run: $(ACCOUNTS)
	docker run -d --name=$(IMAGE) \
		--mount type=bind,source="$(ACCOUNTS)",target=/users.csv,readonly \
		$(IMAGE):$(TAG)

exec:
	docker exec -ti $(IMAGE) /bin/bash

stop:
	docker stop $(IMAGE)
	docker rm $(IMAGE)