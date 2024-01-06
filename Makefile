.PHONY: tar-trafgen tar-dns tar-registry tar-prometheus


BASE = ${PWD}
INFRA = $(BASE)/load-infra
LOAD = $(BASE)/load-generator
CERTS_FOLDER = "load-infra/certs"
SERVER_CERTS_FOLDER = $(CERTS_FOLDER)/servers
CLIENT_CERTS_FOLDER = "$(CERTS_FOLDER)/clients"

tar-trafgen:
	cd $(INFRA)/trafgen-node && \
	tar -cvf  $(INFRA)/trafgen.tar usr && \
	tar -rvf $(INFRA)/trafgen.tar etc && \
	tar -rvf $(INFRA)/trafgen.tar opt && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/trafgen.tar etc && \
	tar -rvf $(INFRA)/trafgen.tar usr && \
	cd $(LOAD)/ && \
	tar -rvf $(INFRA)/trafgen.tar etc


tar-dns:
	cd $(INFRA)/dns && \
	tar -cvf  $(INFRA)/dns.tar usr && \
	tar -rvf $(INFRA)/dns.tar etc && \
	tar -rvf $(INFRA)/dns.tar opt && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/dns.tar etc && \
	tar -rvf $(INFRA)/dns.tar usr 


tar-prometheus:
	cd $(INFRA)/prometheus && \
	tar -cvf  $(INFRA)/prometheus.tar usr && \
	tar -rvf $(INFRA)/prometheus.tar etc && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/prometheus.tar etc && \
	tar -rvf $(INFRA)/prometheus.tar usr 


tar-registry:
	cd $(INFRA)/registry && \
	tar -cvf  $(INFRA)/registry.tar usr && \
	tar -rvf $(INFRA)/registry.tar etc && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/registry.tar etc && \
	tar -rvf $(INFRA)/registry.tar usr 

tar-controller:
	cd $(INFRA)/controller && \
	tar -cvf  $(INFRA)/controller.tar usr && \
	tar -rvf $(INFRA)/controller.tar etc && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/controller.tar etc && \
	tar -rvf $(INFRA)/controller.tar usr 

tar-elk:
	cd $(INFRA)/elk && \
	tar -cvf  $(INFRA)/elk.tar usr && \
	tar -rvf $(INFRA)/elk.tar etc && \
	cd $(INFRA)/all-nodes && \
	tar -rvf $(INFRA)/elk.tar etc && \
	tar -rvf $(INFRA)/elk.tar usr 

tar-basic:
	cd $(INFRA)/all-nodes && \
	tar -cvf $(INFRA)/basic.tar etc && \
	tar -rvf $(INFRA)/basic.tar usr 

SERVER_NAME ?=

tar-docker-server:
	@if [ -z "$(SERVER_NAME)" ]; then \
		echo "error: SERVER_NAME is not set. Please specify the SERVER_NAME variable."; \
	else \
		cp $(SERVER_CERTS_FOLDER)/$(SERVER_NAME)/* $(INFRA)/docker-server/etc/docker/certs/ && \
		cd $(INFRA)/all-nodes && \
		tar -cvf $(INFRA)/docker-server.tar etc && \
		tar -rvf $(INFRA)/docker-server.tar usr && \
		cd $(INFRA)/docker-server && \
		tar -rvf $(INFRA)/docker-server.tar usr && \
		tar -rvf $(INFRA)/docker-server.tar etc; \
	fi


create-ca:
	@$(MAKE) -C  load-infra ca-cert

create-ca-crt:
	@$(MAKE) -C  load-infra ca.crt

SERVERS ?=

servers-cert:
	@if [ -z "$(SERVERS)" ]; then \
		echo "error: SERVERS is not set. Please specify the SERVERS variable."; \
	else \
		for server in $(SERVERS); do \
			if [[ ! -d "$(SERVER_CERTS_FOLDER)/$$server" ]]; then \
				mkdir -p $(SERVER_CERTS_FOLDER)/$$server; \
			fi; \
			make -C load-infra server-cert SERVER=$$server; \
		done; \
	fi


CLIENTS ?=

clients-cert:
	@if [ -z "$(CLIENTS)" ]; then \
		echo "error: CLIENTS is not set. Please specify the CLIENTS variable."; \
	else \
		for client in $(CLIENTS); do \
			if [[ ! -d "$(CLIENT_CERTS_FOLDER)/$$client" ]]; then \
				mkdir -p $(CLIENT_CERTS_FOLDER)/$$client; \
			fi; \
			make -C load-infra client-cert CLIENT=$$client; \
		done; \
	fi
