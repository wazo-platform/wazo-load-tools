IMAGE = wazo-trafgen
TAG = 0.0.1
DOCKERFILE := Dockerfile
build: $(DOCKERFILE)
	.PHONY: build

build: build-trafgen

IMAGE = wazo-trafgen
TAG = 0.0.1
TRAFGENFILE := Dockerfile.trafgen
build-trafgen: $(TRAFGENFILE)
	docker build -t $(IMAGE):$(TAG) -f $(TRAFGENFILE) .

.PHONY: run halt
DOCKERCOMPOSE_FILE := ./Docker-compose.yml
run: $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) up

halt: $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) down
