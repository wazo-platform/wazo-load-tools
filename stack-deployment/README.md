# Automated stack deployment for load testing

These tools will deploy a VM, install wazo stack EUC and populate it with 5000
users.

It uses terraform with openstack provider. If you need another cloud provider
you'll have to adapt the `*.tf` files.

You'll need a valid openstack account with the necessary rights to be able to
create a Virtual Machine and get IPs.

In order to deploy your stack be sure you have a network access to your
openstack instance or cloud provider.
- Edit the vars.tf file to substitute the required fields with your own
  credentials and informations.
- Edit the cloud-init.yml file to put your own public keys.
- Edit the setup.env file with your informations.

Once all files are edited you can deploy your VM:
```sh
terraform init
terraform plan -out plan
terraform apply "plan"
```

or use the makefile:
```sh
make deploy-vm
```

Then run the stack-install.sh script:
```sh
./stack-install.sh
```

or use the make file
```sh
make stack-install
```

you can use the make file to run the 2 steps above in one command
```sh
make all
```

Once the stack is deployed and populated with the users, you can integrate it
into your prometheus instance.
