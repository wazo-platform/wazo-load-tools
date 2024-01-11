.PHONY: deploy-vm stack-install

all: deploy-vm stack-install

deploy-vm: cloud-init.yml vars.tf wazo.tf 
	terraform init
	terraform plan -out plan
	terraform apply "plan"

stack-install: stack-install.sh setup.env
	./stack-install.sh