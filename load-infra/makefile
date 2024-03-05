.PHONY: deploy-docker-server

.PHONY: all server-cert client-cert clean

DIR = certs
CA_DIR = $(DIR)/ca
CLIENTS_DIR = $(DIR)/clients
SERVERS_DIR = $(DIR)/servers
SERVER ?= sever1.load.wazo.io
CLIENT ?= client1.load.wazo.io
DAYS ?= 3650
all: server-cert client-cert

# self signed CA
ca.key: $(CA_DIR)
	openssl genpkey -algorithm RSA -out $(CA_DIR)/ca.key

ca.crt: $(CA_DIR)
	openssl req -x509 -new -nodes -key $(CA_DIR)/ca.key -sha256 -days $(DAYS) -out $(CA_DIR)/ca.crt -subj "/CN=*.load.wazo.io"

# Certs and Key for Docker server
server.key: $(SERVERS_DIR)/$(SERVER)
	openssl genpkey -algorithm RSA -out $(SERVERS_DIR)/$(SERVER)/server.key

server.csr: $(SERVERS_DIR)/$(SERVER)
	openssl req -new -key $(SERVERS_DIR)/$(SERVER)/server.key -out $(SERVERS_DIR)/$(SERVER)/server.csr -subj "/CN=*.load.wazo.io"

server.crt: $(CA_DIR)/ca.key $(CA_DIR)/ca.crt $(SERVERS_DIR)/$(SERVER) server.csr
	openssl x509 -req -in $(SERVERS_DIR)/$(SERVER)/server.csr -CA $(CA_DIR)/ca.crt -CAkey $(CA_DIR)/ca.key -CAcreateserial -out $(SERVERS_DIR)/$(SERVER)/server.crt -days $(DAYS) -sha256

# certs and key for Docker client
client.key: $(CLIENTS_DIR)/$(CLIENT)
	openssl genpkey -algorithm RSA -out $(CLIENTS_DIR)/$(CLIENT)/client.key

client.csr: $(CLIENTS_DIR)/$(CLIENT) client.key
	openssl req -new -key $(CLIENTS_DIR)/$(CLIENT)/client.key -out $(CLIENTS_DIR)/$(CLIENT)/client.csr -subj "/CN=*.load.wazo.io"

client.crt: $(CA_DIR)/ca.key $(CA_DIR)/ca.crt $(CLIENTS_DIR)/$(CLIENT) client.csr
	openssl x509 -req -in $(CLIENTS_DIR)/$(CLIENT)/client.csr -CA $(CA_DIR)/ca.crt -CAkey $(CA_DIR)/ca.key -CAcreateserial -out $(CLIENTS_DIR)/$(CLIENT)/client.crt -days $(DAYS) -sha256

server-cert: server.key server.crt

client-cert: client.crt client.key

ca-cert: ca.key ca.crt

clean:
	rm -f *.crt *.key *.csr *.srl
