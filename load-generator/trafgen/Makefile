.PHONY: build

IMAGE = wazo-trafgen
TAG = 0.0.1
DOCKERFILE := Dockerfile
build: $(DOCKERFILE)
	docker build -t $(IMAGE):$(TAG) -f $(DOCKERFILE) .
