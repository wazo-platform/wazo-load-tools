PHONY: build run stop clean

LB_CONFIG_GEN_SCRIPT = gen-lb-config.sh
# LAST_CONTAINER from 0 to 99
LAST_CONTAINER ?= 0
# TRAFGEN_NODES from 1 to 10
TRAFGEN_NODES ?= 10
DOCKERFILE = Dockerfile
IMAGE = trafgen-lb
TAG ?= 0.0.3
CONTAINER_NAME = $(IMAGE)
CONTAINERS = $(shell echo $$(( $(LAST_CONTAINER) + 1 )))
CLUSTER_SIZE = $(shell echo $$(( $(CONTAINERS) * $(TRAFGEN_NODES) )))

build: clean certs $(DOCKERFILE) $(LB_CONFIG_GEN_SCRIPT)
	./$(LB_CONFIG_GEN_SCRIPT) $(LAST_CONTAINER) $(TRAFGEN_NODES)
	docker build -t $(IMAGE)-$(CLUSTER_SIZE):$(TAG) -f $(DOCKERFILE) .

run: stop
	docker run -d -p 9999:443 -p 9998:80 --rm --name $(CONTAINER_NAME) $(IMAGE)-$(CLUSTER_SIZE):$(TAG)

stop:
	-docker stop $(CONTAINER_NAME)

KEY = certs/server.key
CERT = certs/server.pem
CSR = certs/server.csr
CN ?= example.com
certs: clean
	mkdir certs
	openssl genrsa -out $(KEY) 2048
	openssl req -new -key $(KEY) -out $(CSR) -subj "/CN=$(CN)"
	openssl x509 -req -in $(CSR) -signkey $(KEY) -out $(CERT) -days 36500

clean:
	-rm *.generated
	-rm -rf certs
