#!/usr/bin/env bash
set -e

batcher_address=$(cat batcher.addr)
collat_address=$(cat collat.addr)

socket_path=$(yq '.socket_path' ../config.yaml)
network=$(yq '.network' ../config.yaml)
cli=$(yq '.cli_path' ../config.yaml)

echo -e "\n \033[1;34mBatcher: ${batcher_address} \033[0m \n";
${cli} query utxo --socket-path ${socket_path} --address ${batcher_address} ${network}

echo -e "\n \033[1;35mCollateral: ${collat_address} \033[0m \n";
${cli} query utxo --socket-path ${socket_path} --address ${collat_address} ${network}