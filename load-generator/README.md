# load generator
## Create the users and configure the xivo-load-test tool
This has to be done only once, before being able to perform any tests. 
Simply run to creating 500 users
> make create_500_users

for 1000 users
> make create_1000_users

and for 5000 users
> make create_5000_users

It will create the number of users labelled by the target and then it will build, with these users, 
the trafgen container that will be used for the tests. 

## more details
about trafgen see [load-generator/trafgen/README.md](load-generator/trafgen/README.md)
about user creation see [load-generator/users/README.md](load-generator/users/README.md)