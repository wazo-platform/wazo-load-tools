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

.PHONY: run halt load_test prereqs load_2_sides_tests stop_2_sides_tests

SCRIPT ?= ./start-tests.sh
DOCKERCOMPOSE_FILE ?= ./Docker-compose.yml
CALLER_CONTAINER ?= trafgen-caller
CALLER_SCENARIO ?= send-sip-register
CALLEE_CONTAINER ?= trafgen-callee
CALLEE_SCENARIO ?= answer-then-wait

load_2_sides_tests: run load_test_callee load_test_caller

stop_2_sides_tests: halt

prereqs:
	-mkdir -p trafgen/logs/caller
	-mkdir -p trafgen/logs/callee

run: prereqs $(DOCKERCOMPOSE_FILE)
	docker compose -f $(DOCKERCOMPOSE_FILE) up &

halt: $(DOCKERCOMPOSE_FILE)
	docker compose -f $(DOCKERCOMPOSE_FILE) down

load_test_caller: $(SCRIPT)
	$(SCRIPT) $(CALLER_CONTAINER) $(CALLER_SCENARIO)

load_test_callee: $(SCRIPT)
	$(SCRIPT) $(CALLEE_CONTAINER) $(CALLEE_SCENARIO)

stop_test:
	docker stop trafgen-callee; docker rm trafgen-callee
	docker stop trafgen-caller; docker rm trafgen-caller
