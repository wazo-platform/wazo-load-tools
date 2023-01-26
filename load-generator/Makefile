create_500_users:
	cd users && make usergen500 && make confgen CONFIG=config.500.py
	cp users/config.5000.py trafgen/config.py
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
	-mkdir trafgen/logs

DOCKERCOMPOSE_FILE := ./Docker-compose.yml
run: prereqs $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) up &

halt: $(DOCKERCOMPOSE_FILE)
	docker-compose -f $(DOCKERCOMPOSE_FILE) down

ENVS ?= trafgen/trafgen.env
load_test: $(ENVS)
	docker exec -it --env-file $(ENVS) trafgen bash -c "/trafgen/load-tests.sh"