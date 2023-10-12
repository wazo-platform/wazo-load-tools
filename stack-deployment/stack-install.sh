#!/bin/bash -x
# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

PARAMS=""
NO_WIZARD=0

while (( $# )); do
  case "$1" in
    --stack)
      if [ -n "$2" ] && [ ${2:0:1} != "-" ]; then
        STACK_IP=$2
        shift 2
      else
        echo "Error: Argument for $1 is missing" >&2
        exit 1
      fi
      ;;
    --no-wizard)
      NO_WIZARD=1
      shift
      ;;
    *)
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

eval set -- "$PARAMS"


source ./setup.env
if [ -z $STACK_IP ]; then
  STACK_IP=$(jq -r '.resources[] | select(.type == "openstack_networking_floatingip_v2") | .instances[0].attributes.address' terraform.tfstate)
fi

if [ -z $STACK_IP ];then
    echo "missing stack ip. check the terraform.state file"
    exit 1
fi

# Start probing the stack
CODE=500
while [ $CODE -ne 200 ]
do
    CODE=$(curl -s -o /dev/null -w "%{http_code}" -k https://$STACK_IP/api/confd/1.1/wizard)
done

if [ $NO_WIZARD -eq "0" ]; then
  CONFD_JSON=confd.json
  curl -s -X GET \
    --header 'Accept: application/json' \
    -k -o $CONFD_JSON "https://$STACK_IP:$STACK_PORT/api/confd/1.1/wizard/discover"

  STACK_PRIVATE_IP=$(jq -r '.interfaces[0].ip_address' $CONFD_JSON)
  if [ -z $STACK_PRIVATE_IP ];then
      echo "missing private ip. check the result of GET 'https://$STACK_IP:$STACK_PORT/api/confd/1.1/wizard/discover'"
      exit 1
  fi

  # Generate the setup file from the template
  template_file="./setup.json.tpl"
  output_file="./setup.json"
  sed -e "s/__ENGINE_PASSWORD__/\"$ENGINE_PASSWORD\"/" \
      -e "s/__STACK_IP__/\"$STACK_IP\"/" \
      -e "s/__STACK_PORT__/$STACK_PORT/" \
      -e "s/__PORTAL_FQDN__/\"$PORTAL_FQDN\"/" \
      -e "s/__NAME_INSTANCE__/\"$NAME_INSTANCE\"/" \
      -e "s/__PORTAL_PORT__/$PORTAL_PORT/" \
      -e "s/__PORTAL_ID__/\"$PORTAL_ID\"/" \
      -e "s/__PORTAL_PASSWORD__/\"$PORTAL_PASSWORD\"/" \
      -e "s/__STACK_PRIVATE_IP__/\"$STACK_PRIVATE_IP\"/" \
      "$template_file" > "$output_file"

  # Pause before continuing stack configuration. The stack needs a bit of time to get ready  !
  DELAY=400
  sleep $DELAY
  # Setup the stack
  curl -s -k -XPOST https://$STACK_IP:$STACK_PORT/api/setupd/1.0/setup \
    -H "Content-Type: application/json" \
    -d @$output_file
fi

# Create the required token
TOKEN_JSON=token.json
curl -s -XPOST -o $TOKEN_JSON \
  --header 'Content-Type: application/json' \
  -u "root:$ENGINE_PASSWORD" \
  --header 'Accept: application/json' \
  -d '{"access_type": "online", "backend": "wazo_user", "expiration": 600000}' \
  "https://$STACK_IP:$STACK_PORT/api/auth/0.1/token" -k
INITIAL_TOKEN=$(jq -r .data.token token.json)


# Create the tenant uuid
TENANT_JSON=tenant.json
TENANT_NAME_SUFFIX=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 10 ; echo '')
TENANT_NAME="Load-${TENANT_NAME_SUFFIX}"
curl -s -o $TENANT_JSON -X POST \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  -d "$(jq -Mcn '$ARGS.named' --arg name $TENANT_NAME)" \
  "https://$STACK_IP:$STACK_PORT/api/auth/0.1/tenants" \
  -k -H "X-Auth-Token: $INITIAL_TOKEN"

TENANT_UUID=$(jq -r .uuid $TENANT_JSON)


# Create the webrtc UUID
WEBRTC_UUID_JSON=werbrtc_sip_uuid.json
for n in $(seq 5); do
  curl -s -X GET -o $WEBRTC_UUID_JSON \
    --header 'Accept: application/json' \
    --header "Wazo-Tenant: $TENANT_UUID" \
    --header "X-Auth-Token: $INITIAL_TOKEN" \
    "https://$STACK_IP:$STACK_PORT/api/confd/1.1/endpoints/sip/templates?search=webrtc" -k
  WEBRTC_UUID=$(jq -r .items[].uuid werbrtc_sip_uuid.json)
  if [ -z "$WEBRTC_UUID" ]; then
    sleep 1
  else
    break
  fi
done

# Create the internal tenant's context
CONTEXT_JSON=context.json
LABEL=internal
START=1000
END=9999
INCALL_PREFIX=123456
curl -s -o $CONTEXT_JSON -X POST \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  --header "Wazo-Tenant: $TENANT_UUID" \
  --header "X-Auth-Token: $INITIAL_TOKEN" \
  -d "{\"enabled\": true, \"label\": \"$LABEL\", \"type\": \"internal\", \"user_ranges\": [{\"end\": \"$END\", \"start\": \"$START\"}]}" \
  "https://$STACK_IP:$STACK_PORT/api/confd/1.1/contexts" -k

if [ -z $CONTEXT_JSON ]; then
  echo "context file is missing, can't continue"
fi
CONTEXT=$(jq -r .name $CONTEXT_JSON)

# Create the incoming call context
INCALL_CONTEXT_JSON=incall_context.json
curl -s -o $INCALL_CONTEXT_JSON -X POST \
  --header 'Content-Type: application/json' \
  --header 'Accept: application/json' \
  --header "Wazo-Tenant: $TENANT_UUID" \
  --header "X-Auth-Token: $INITIAL_TOKEN" \
  -d "{\"enabled\": true, \"label\": \"$LABEL\", \"type\": \"incall\", \"incall_ranges\": [{\"end\": \"${INCALL_PREFIX}${END}\", \"start\": \"${INCALL_PREFIX}${START}\"}]}" \
  "https://$STACK_IP:$STACK_PORT/api/confd/1.1/contexts" -k

if [ -z $INCALL_CONTEXT_JSON ]; then
  echo "context file is missing, can't continue"
fi
INCALL_CONTEXT=$(jq -r .name $INCALL_CONTEXT_JSON)

cd ../load-generator/users/
cat <<EOF >usergen_params.json
{
  "uuid":"$TENANT_UUID",
  "token":"$INITIAL_TOKEN",
  "ip":"$STACK_IP",
  "webrtc_uuid":"$WEBRTC_UUID",
  "context":"$CONTEXT",
  "incall_context": "$INCALL_CONTEXT",
  "incall_prefix": "$INCALL_PREFIX"
}
EOF
make usergen5000
