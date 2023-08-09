# Automated stack deployment for load testing

It uses terraform with openstack provider. If you need another cloud provider you'll have to adapt
the *.tf files.

You'll need a valid openstack account with the necessary rights to be able to create a Virtual Machine
and get IPs.

In order to deploy your stack be sure you have a network access to your openstack insrance or cloud provider.
Edit the vars.tf file to substitute the required fields with your own credentials and informations.
Edit the cloud-init.yml file to put your own public keys.
Edit the setup.env file with your informations.

Once all files are edited you can deploy your VM:
```
terraform init
terraform plan -out plan
terraform apply "plan"
```

or use the makefile:
```
make deploy-vm
```

Then run the stack-install.sh script:
```
./stack-install.sh
```

or use the make file
```
make stack-install
```
you can use the make file to run the 2 steps above in one command
```
make all
```
