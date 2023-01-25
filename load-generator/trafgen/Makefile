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

.PHONY: run halt load_test load_configure
DOCKERCOMPOSE_FILE := ./Docker-compose.yml
run: prereqs $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) up &

halt: $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) down


load_test: trafgen.env
	docker exec -it --env-file trafgen.env trafgen bash -c "/trafgen/load-tests.sh"

.PHONY: usergen500 usergen1000 usergen5000
USERGEN_SCRIPT := ./usergen.sh
USER_TEMPLATE := ./user.json.tpl
PARAMS_FILE := ./usergen_params.json

usergen500: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	@for i in $$(seq 1 500); do ./usergen.sh $$i $(PARAMS_FILE); done

usergen1000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	@for i in $$(seq 1 1000); do ./usergen.sh $$i $(PARAMS_FILE); done

usergen5000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	@for i in $$(seq 1 5000); do ./usergen.sh $$i $(PARAMS_FILE); done
