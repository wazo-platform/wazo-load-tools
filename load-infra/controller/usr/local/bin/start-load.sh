#!/bin/bash

declare -A content

while IFS="=" read -r key value; do content["$key"]=$value; done < <(
  yq '.street_address | to_entries | map([.key, .value] | join("=")) | .[]' personal_data.yaml
)

for key in "${!content[@]}"; do printf "key %s, value %s\n" "$key" "${content[$key]}"; done