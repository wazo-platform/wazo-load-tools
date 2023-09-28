.PHONY: usergen500 usergen1000 usergen5000
USERGEN_SCRIPT ?= ./usergen.sh
USER_TEMPLATE ?= ./user.json.tpl
PARAMS_FILE ?= ./usergen_params.json

usergen500: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	@for i in $$(seq 1 501); do ./usergen.sh $$i $(PARAMS_FILE); done

usergen1000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	@for i in $$(seq 1 1001); do ./usergen.sh $$i $(PARAMS_FILE); done

usergen5000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	@for i in $$(seq 1000 6000); do ./usergen.sh $$i $(PARAMS_FILE); done

usergen10000: $(USERGEN_SCRIPT) $(USER_TEMPLATE)
	@for i in $$(seq 10000 20000); do ./usergen.sh $$i $(PARAMS_FILE); done

.PHONY: confgen
USERS_CSV ?= user-files/users.csv
TEMPLATE ?= config.py.tpl
CONFIG ?= config.generated.py
confgen: $(USERS_CSV) $(TEMPLATE) 
	./configen.sh $(USERS_CSV) $(TEMPLATE) $(CONFIG)
