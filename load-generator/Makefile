create_500_users:
	cd users && make usergen500 && make confgen CONFIG=config.500.py
	cp users/config.500.py trafgen/config.py
	cd trafgen/ && make build

create_1000_users:
	cd users && make usergen1000 && make confgen CONFIG=config.1000.py
	cp users/config.1000.py trafgen/config.py
	cd trafgen/ && make build

create_5000_users:
	cd users && make usergen5000 && make confgen CONFIG=config.5000.py
	cp users/config.5000.py trafgen/config.py
	cd trafgen/ && make build

.PHONY: run halt load_test prereqs

prereqs:
	-mkdir -p trafgen/logs/caller
	-mkdir -p trafgen/logs/callee

DOCKERCOMPOSE_FILE := ./Docker-compose.yml
run: prereqs $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) up &

halt: $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) down

SCENARIO_CALLER ?= send-sip-register
load_test_caller:
	docker exec  --env SCENARIO=$(SCENARIO_CALLER) trafgen-caller bash -c "/trafgen/load-tests.sh"

SCENARIO_CALLEE ?= answer-then-wait
load_test_caller:
	docker exec  --env SCENARIO=$(SCENARIO_CALLEE) trafgen-callee bash -c "/trafgen/load-tests.sh"

stop_test:
	docker stop trafgen; docker rm trafgen
