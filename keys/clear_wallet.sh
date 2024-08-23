#!/usr/bin/env bash
set -e
#
rm ../tmp/tx.signed || true

socket_path=$(yq '.socket_path' ../config.yaml)
network=$(yq '.network' ../config.yaml)
cli=$(yq '.cli_path' ../config.yaml)


# Addresses
sender_path="batcher"
sender_address=$(cat ${sender_path}.addr)
receiver_address=$(yq '.profit_address' ../config.yaml)
#
# exit
#
echo -e "\033[0;36m Gathering UTxO Information  \033[0m"
${cli} query utxo \
    --socket-path ${socket_path} \
    ${network} \
    --address ${sender_address} \
    --out-file ../tmp/sender_utxo.json

TXNS=$(jq length ../tmp/sender_utxo.json)
if [ "${TXNS}" -eq "0" ]; then
   echo -e "\n \033[0;31m NO UTxOs Found At ${sender_address} \033[0m \n";
   exit;
fi
alltxin=""
TXIN=$(jq -r --arg alltxin "" 'keys[] | . + $alltxin + " --tx-in"' ../tmp/sender_utxo.json)
sender_tx_in=${TXIN::-8}
echo Sender UTxO: ${sender_tx_in}
#
# exit
#
echo -e "\033[0;36m Building Tx \033[0m"
FEE=$(${cli} transaction build \
    --socket-path ${socket_path} \
    --babbage-era \
    --out-file ../tmp/tx.draft \
    --change-address ${receiver_address} \
    --tx-in ${sender_tx_in} \
    ${network})

IFS=':' read -ra VALUE <<< "${FEE}"
IFS=' ' read -ra FEE <<< "${VALUE[1]}"
FEE=${FEE[1]}
echo -e "\033[1;32m Fee: \033[0m" $FEE
#
# exit
#
echo -e "\033[0;36m Signing \033[0m"
${cli} transaction sign \
    --signing-key-file ${sender_path}.skey \
    --tx-body-file ../tmp/tx.draft \
    --out-file ../tmp/tx.signed \
    ${network}
#
# exit
#
echo "Press 1 to submit or any other key to exit."
read -rsn1 input

if [[ "$input" == "1" ]]; then
    echo -e "\033[0;36m Submitting \033[0m"
    ${cli} transaction submit \
        --socket-path ${socket_path} \
        ${network} \
        --tx-file ../tmp/tx.signed
else
    echo "Exiting"
    exit 0;
fi

tx=$(${cli} transaction txid --tx-file ../tmp/tx.signed)
echo "Tx Hash:" $tx