.PHONY: build prereqs

prereqs:
	-mkdir logs

build: build-trafgen-sipp build-trafgen

SIPP_IMAGE = wazo-trafgen-sipp
TAG = 0.0.1
TRAFGENSIPPFILE := Dockerfile.sipp
build-trafgen-sipp: $(TRAFGENSIPPFILE)
	docker build -t $(SIPP_IMAGE):$(TAG) -f $(TRAFGENSIPPFILE) .

TRAFGEN_IMAGE = wazo-trafgen
TAG = 0.0.1
TRAFGENFILE := Dockerfile.trafgen
build-trafgen: $(TRAFGENFILE)
	docker build -t $(TRAFGEN_IMAGE):$(TAG) -f $(TRAFGENFILE) .

.PHONY: run halt
DOCKERCOMPOSE_FILE := ./Docker-compose.yml
run: prereqs $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) up

halt: $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) down
