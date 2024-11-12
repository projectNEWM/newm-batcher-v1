#!/usr/bin/env bash

set -e

network=$(yq '.network' ../config.yaml)
cli=$(yq '.cli_path' ../config.yaml)
socket_path=$(yq '.socket_path' ../config.yaml)

batcher_address=$(cat ../keys/batcher.addr)
batcher_pkh=$(cat ../keys/batcher.hash)
collat_pkh=$(cat ../keys/collat.hash)
collat_utxo=$(yq '.collat_utxo' ../config.yaml)
profit_address=$(yq '.profit_address' ../config.yaml)

# place batcher and band utxo info here, you can find this from the previous tx
batcher_utxo=""
band_utxo=""

# assumes an already complete band
assets="1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e73746572436f6e647563746f72323739 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e73746572436f756e7472793739 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e73746572446973636f323739 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e73746572446f75626c65426173733632 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e737465724472756d6d6572353439 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e737465724b506f703533 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e7374657250657263757373696f6e323234 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e7374657250756e6b3230 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e7374657252616e63686572613837 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e73746572536f6e677772697465723435 + 1 b3e0f7538ba97893b0fea85409cecfbf300d164954da2728406bb571.4e45574d6f6e7374657253776973734c616e646c65723135 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e73746572444a313937 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e73746572466c616d656e636f3334 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e7374657248656176794d6574616c313337 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e7374657248656c6c6f333138 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e73746572486970486f70343634 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e737465724a617a7a313839 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e737465724f70657261323632 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e737465725069616e697374343730 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e73746572526567676165313939 + 1 e92f13e647afa0691006fb98833b60b61e6eb88d6180e7537bdb94a6.4e45574d6f6e73746572526f636b3731"

IFS='#' read -ra array <<< "${band_utxo}"

batcher_token_prefix="affab1e0005e77ab1e"
complete_token_prefix="c011ec7ed000a55e75"
batcher_policy=$(yq '.batcher_policy' ../config.yaml)
cd ..
batcher_token_name=$(python3 -c "from src.utility import generate_token_name; tkn=generate_token_name('${array[0]}', ${array[1]}, '${batcher_token_prefix}'); print(tkn)")
complete_token_name=$(python3 -c "from src.utility import generate_token_name; tkn=generate_token_name('${array[0]}', ${array[1]}, '${complete_token_prefix}'); print(tkn)")
cd scripts
complete_token="1 ${batcher_policy}.${complete_token_name}"

batcher_token="1 ${batcher_policy}.${batcher_token_name}"

echo $complete_token
echo $batcher_token

min_utxo=$(${cli} conway transaction calculate-min-required-utxo \
    --protocol-params-file tmp/protocol.json \
    --tx-out-inline-datum-file ../tmp/wallet-datum.json \
    --tx-out="${band_address} + 5000000 + ${assets} + ${complete_token}" | tr -dc '0-9')

band_address_output="${band_address} + ${min_utxo} + ${assets} + ${complete_token}"
batcher_address_out="${batcher_address} + 5000000 + ${batcher_token}"

band_ref_utxo=$(yq '.band_ref_utxo' ../config.yaml)
batcher_ref_utxo=$(yq '.batcher_ref_utxo' ../config.yaml)

data_address=$(yq '.data_address' ../config.yaml)
data_policy=$(yq '.data_policy' ../config.yaml)
data_asset=$(yq '.data_asset' ../config.yaml)
data_ref_utxo=$(${cli} conway query utxo --socket-path ${socket_path} --address ${data_address} ${network} --output-json | jq --arg pid "${data_policy}"  --arg tkn "${data_asset}" -r 'to_entries[] | select(.value.value[$pid][$tkn] == 1) | .key' )

cp ../batcher_token.cbor.hex ../metadata.hex
sed -i "s/policy_here000000000000000000000000000000000000000000000/$batcher_policy/g" ../metadata.hex
sed -i "s/affab1e000000000000000000000000000000000000000000000000000000000/$batcher_token_name/g" ../metadata.hex
xxd -r -p ../metadata.hex > ../batcher_token.cbor

exit

echo -e "\033[0;36m Building Tx \033[0m"
FEE=$(${cli} conway transaction build \
    --socket-path ${socket_path} \
    --out-file ../tmp/tx.draft \
    --change-address ${profit_address} \
    --read-only-tx-in-reference="${data_ref_utxo}" \
    --tx-in-collateral="${collat_utxo}" \
    --tx-in ${batcher_utxo} \
    --tx-in ${band_utxo} \
    --spending-tx-in-reference="${band_ref_utxo}" \
    --spending-plutus-script-v3 \
    --spending-reference-tx-in-inline-datum-present \
    --spending-reference-tx-in-redeemer-file ../tmp/mint-band-redeemer.json \
    --tx-out="${batcher_address_out}" \
    --tx-out="${band_address_output}" \
    --tx-out-inline-datum-file ../tmp/wallet-datum.json  \
    --required-signer-hash ${batcher_pkh} \
    --required-signer-hash ${collat_pkh} \
    --mint="${batcher_token} + ${complete_token}" \
    --mint-tx-in-reference="${batcher_ref_utxo}" \
    --mint-plutus-script-v3 \
    --policy-id="${batcher_policy}" \
    --mint-reference-tx-in-redeemer-file ../tmp/mint-batcher-redeemer.json \
    --metadata-cbor-file ../batcher_token.cbor \
    ${network})

IFS=':' read -ra VALUE <<< "${FEE}"
IFS=' ' read -ra FEE <<< "${VALUE[1]}"
echo -e "\033[1;32m Fee:\033[0m" $FEE

echo -e "\033[0;36m Signing \033[0m"
${cli} conway transaction sign \
    --signing-key-file ../keys/batcher.skey \
    --signing-key-file ../keys/collat.skey \
    --tx-body-file ../tmp/tx.draft \
    --out-file ../tmp/tx.signed \
    ${network}

echo -e "\033[0;36m Submitting \033[0m"
${cli} conway transaction submit \
    --socket-path ${socket_path} \
    ${network} \
    --tx-file ../tmp/tx.signed