#!/usr/bin/env bash

socket=$(yq '.socket_path' config.yaml)
network=$(yq '.network' config.yaml)
cli=$(yq '.cli_path' config.yaml)
port=$(yq '.node_port' config.yaml)

# Determine the magic value based on the network
if [[ "$network" == "--mainnet" ]]; then
    magic="764824073"
else
    # Extract the integer after testnet-magic
    magic=$(echo "$network" | grep -oP 'testnet-magic \K\d+')
fi

# Loop until the node is connected
while true; do
    # Ping the node
    output=$(${cli} ping \
    --count 1 \
    --port ${port} \
    --magic $magic \
    --unixsock $socket \
    --json \
    --quiet \
    --query-versions)

    # Check the result
    if echo "$output" | grep -q '"queried_versions":'; then
        echo "Cardano node is connected and ready."
        exit 0
    else
        echo "Waiting for Cardano node to connect..."
        sleep 5
    fi
done
