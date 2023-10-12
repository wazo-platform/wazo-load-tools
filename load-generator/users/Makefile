.PHONY: usergen10 usergen500 usergen1000 usergen5000 usergen10000
USERGEN_SCRIPT ?= ./usergen.sh
USER_TEMPLATE ?= ./user.json.tpl
PARAMS_FILE ?= ./usergen_params.json

usergen10: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	./create_users.py 1000 10 $(PARAMS_FILE)

usergen500: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	./create_users.py 1000 500 $(PARAMS_FILE)

usergen1000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	./create_users.py 1000 1000 $(PARAMS_FILE)

usergen5000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	./create_users.py 1000 5000 $(PARAMS_FILE)

usergen10000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	./create_users.py 10000 10000 $(PARAMS_FILE)

.PHONY: confgen
USERS_CSV ?= user-files/users.csv
TEMPLATE ?= config.py.tpl
CONFIG ?= config.generated.py
confgen: $(USERS_CSV) $(TEMPLATE) 
	./configen.sh $(USERS_CSV) $(TEMPLATE) $(CONFIG)
