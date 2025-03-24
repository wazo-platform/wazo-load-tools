# Generator

Tools to generate load on wazo

## Users

Generate and create wazo users

```shell
./users/generate-users.py -n10 -f csv -c users/config.yml -o users/users.csv
./users/create-users.py -s <wazo-ip> -p <password> -u users/users.csv -f csv -c users/config.yml
```
