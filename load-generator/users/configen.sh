#!/bin/bash -x
USER_FILE=${1:-user-files/users.csv}
TEMPLATE=${2:-config.py.tpl}
CONFIG=${3:-config.generated.py}
OFFSET=${4:-250}
START_SEQ=${5:-2000}


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

cat >>$CONFIG <<EOF
    ],
    expires = 120,
)

scenarios.call_auth_then_wait = dict(
    lines = [
EOF

for user in $USERS;do
    read -r username password exten< <(awk -F";" '{print $1, $2, $3}' <<< "$user")
    CURRENT=$(( $exten-1000 ))
    if [ $CURRENT -le $OFFSET ];then
        callee=$(( $exten+$OFFSET ))
        echo "        {'username': '$username', 'password': '$password', 'exten': '$exten', 'callee_exten': '$callee'}," >> $CONFIG
    else
        break
    fi
done

cat >>$CONFIG <<EOF
    ],
    expires = 3600,
)

scenarios.answer_reg_then_wait = dict(
    bind_port = bind_port,
    ring_time = pause,
    codec = codec,
    rtp = rtp,
    lines = [

EOF

for user in $USERS;do
    read -r username password exten< <(awk -F";" '{print $1, $2, $3}' <<< "$user")
    CURRENT=$(( $exten-1000 ))
    if [ $CURRENT -gt $OFFSET ];then
        echo "        {'username': '$username', 'password': '$password', 'exten': '$exten'}," >> $CONFIG
    fi
done

cat >>$CONFIG <<EOF
    ],
    expires = 3600,
)
EOF
