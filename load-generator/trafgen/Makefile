.PHONY: build prereqs

build: build-trafgen-sipp build-trafgen

SIPP_IMAGE = wazo-trafgen-sipp
TAG = 0.0.1
TRAFGENSIPPFILE ?= Dockerfile.sipp
build-trafgen-sipp: $(TRAFGENSIPPFILE)
	docker build -t $(SIPP_IMAGE):$(TAG) -f $(TRAFGENSIPPFILE) .

TRAFGEN_IMAGE = wazo-trafgen
TAG = 0.0.1
TRAFGENFILE ?= Dockerfile.trafgen
build-trafgen: $(TRAFGENFILE)
	docker build -t $(TRAFGEN_IMAGE):$(TAG) -f $(TRAFGENFILE) .
