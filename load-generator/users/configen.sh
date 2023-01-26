#!/bin/bash
USER_FILE=${1:-user-files/users.csv}
TEMPLATE=${2:-config.py.tpl}
CONFIG=${3:-config.generated.py}

# config_gen() will use the freshly created users to feed the config.py file necessary
# to xivo-load-tester to perform its tests.
config_gen () {
    local user_string=$1
    local config=$2
    read -r username password < <(awk -F";" '{print $1, $2}' <<< "$user_string")
    echo "        {'username': '$username', 'password': '$password'}," >> $config

}

cp $TEMPLATE $CONFIG
USERS=$(cat $USER_FILE)
for user in $USERS;do
    config_gen $user $CONFIG
done

echo "    ]," >> $CONFIG
echo "    expires = 120," >> $CONFIG
echo ")" >> $CONFIG
