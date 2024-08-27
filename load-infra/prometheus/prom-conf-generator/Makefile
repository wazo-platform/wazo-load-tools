.PHONY: install clean

VENV_PATH = /opt/prom-config-generator

install:
	mkdir -p $(VENV_PATH)
	python3 -mvenv $(VENV_PATH)
	. $(VENV_PATH)/bin/activate; pip install -r requirements.txt; pip install .
	ln -s $(VENV_PATH)/bin/prom-conf-generator /usr/local/bin/prom-conf-generator

clean:
	rm -f /usr/local/bin/prom-conf-generator
	rm -rf $(VENV_PATH)
