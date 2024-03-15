PHONY: build run stop clean

all: bump-version build clean


DOCKER_FUNCTIONS ?= docker-manager
DOCKERFILE = Dockerfile
IMAGE = trafgen-lb
VERSION_FILE=version
VERSION ?= $(shell cat $(VERSION_FILE))
# SEMVER cat take the following values: patch|minor|major
SEMVER ?= patch
CONTAINER_NAME = $(IMAGE)
IMAGES_BUILD_DIR = .images_built

MAKEFLAGS += --silent
pause:
	@bash -c 'read -n 1 -s -r -p "Hit any key to continue"'
	@echo

show-version: $(VERSION_FILE)
	@echo "Current version is: $(VERSION)"

show-version-and-pause: show-version pause

# ACTION can take the following values:
#      - inc: for incremeting the version
#      - dec: for decrementing the version
ACTION ?= inc
control-version: $(VERSION_FILE)
	mv $(VERSION_FILE) $(VERSION_FILE).prev
	-./semverctl $(ACTION)  $(SEMVER) $(VERSION) > $(VERSION_FILE)
	if [ ! -s version ]; then  mv $(VERSION_FILE).prev $(VERSION_FILE); fi

down-version:
	$(MAKE) control-version ACTION=dec

bump-version:
	$(MAKE) control-version ACTION=inc

NEW_VERSION ?= 0.0.0
set-version:
	$(MAKE) control-version ACTION=set SEMVER=version VERSION=$(NEW_VERSION)

down-version-validation:
	$(MAKE) show-version-and-pause
	$(MAKE) control-version ACTION=dec
	$(MAKE) show-version

bump-version-validation:
	$(MAKE) show-version-and-pause
	$(MAKE) control-version ACTION=inc
	$(MAKE) show-version

MAINTAINER ?= "dev@wazo.io"
# IMAGE STATUS could be: dev|prod|test|donotuse|deprecated
IMAGE_STATUS ?= dev
API_DOCKERFILE_TEMPLATE ?= Dockerfile.tmpl
API_DOCKERFILE ?= Dockerfile

.PHONY: build-dockerfile

build-dockerfile: $(API_DOCKERFILE_TEMPLATE)
	sed -e 's/__MAINTAINER__/$(MAINTAINER)/g' \
	    -e 's/__STATUS__/$(IMAGE_STATUS)/g' \
	    $(API_DOCKERFILE_TEMPLATE) > $(API_DOCKERFILE)

build: build-dockerfile bump-version build-image mark-image

TAG ?= $(shell cat $(VERSION_FILE))

build-image: clean certs $(DOCKERFILE) $(LB_CONFIG_GEN_SCRIPT)
#	./$(LB_CONFIG_GEN_SCRIPT) $(LAST_CONTAINER) $(TRAFGEN_NODES)
	docker build -t $(IMAGE):$(TAG) -f $(DOCKERFILE) .

LAST_BUILD_FILE = .last_image_built
mark-image:
	echo $(TAG) >> $(IMAGES_BUILD_DIR)/$(IMAGE)
	echo $(IMAGE):$(TAG) > $(LAST_BUILD_FILE)

REGISTRY ?= registry.load.wazo.io
PORT ?= 5000
LAST_BUILD = $(shell cat $(LAST_BUILD_FILE))
push: $(LAST_BUILD_FILE)
	if [ ! -s $(LAST_BUILD_FILE) ]; then \
		echo "Error: empty file"; \
	else \
		docker tag $(LAST_BUILD) $(REGISTRY):$(PORT)/$(LAST_BUILD); \
		docker push $(REGISTRY):$(PORT)/$(LAST_BUILD); \
	fi

commit: $(LAST_BUILD_FILE) $(VERSION_FILE)
	if [ ! -s $(LAST_BUILD_FILE) ] || [ ! -s $(VERSION_FILE) ]; then
		echo "Error: empty file detected"; \
	else \
		BRANCH="trafgen-lb-$(LAST_BUILD)""; \
		git checkout -b $$BRANCH; \
		git add $(LAST_BUILD_FILE) $(VERSION_FILE); \
		git commit -m "trafgen load balancer docker image update"; \
		git push --set-upstream origin $$BRANCH; \
	fi


IMAGE_NAME ?= $(shell cat $(LAST_BUILD_FILE))
run:

	docker run -d -p 9999:443 -p 9998:80 --rm  $(IMAGE_NAME)

stop:
	-docker stop $(CONTAINER_NAME) >2&

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
