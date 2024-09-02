#!/usr/bin/env bash
set -e

network=$(yq '.network' ../config.yaml)
cli=$(yq '.cli_path' ../config.yaml)
addr=$(yq '.addr_path' ../config.yaml)

if [ -e "batcher.skey" ]; then
  echo -e "\033[1;31m\nBatcher Keys Exists\n\033[0m"
  if [ -e "collat.skey" ]; then
    echo -e "\033[1;31m\nCollateral Keys Exists\n\033[0m"
    exit 1;
  fi
  exit 1;
fi

if [ -e "collat.skey" ]; then
  echo -e "\033[1;31m\nCollateral Keys Exists\n\033[0m"
  exit 1;
fi

echo "Press 1 to generate a wallet, 2 to load a wallet, or any other key to exit."
read -rsn1 input

if [[ "$input" == "1" ]]; then
    echo -e "\033[1;35m\nGenerating Wallet...\n\033[0m"
    echo -e "\033[1;36m\nWrite Down These Words\n\033[0m"
    seed_phrase=$(${addr} recovery-phrase generate --size 24)
    echo $seed_phrase
    root=$(echo $seed_phrase | ${addr} key from-recovery-phrase Shelley)
    
    # batcher
    echo $root | ${addr} key child 1852H/1815H/0H/0/0 > batcher.xsk
    ${cli} key convert-cardano-address-key --shelley-payment-key --signing-key-file batcher.xsk --out-file batcher.skey
    rm batcher.xsk
    ${cli} key verification-key --signing-key-file batcher.skey --verification-key-file batcher.vkey
    ${cli} address key-hash --payment-verification-key-file batcher.vkey > batcher.hash
    ${cli} address build --payment-verification-key-file batcher.vkey ${network} --out-file batcher.addr
    echo -e "\033[1;37m\nBatcher Address: $(cat batcher.addr)\n\033[0m"
    
    # collateral
    echo $root | ${addr} key child 1852H/1815H/0H/0/1 > collat.xsk
    ${cli} key convert-cardano-address-key --shelley-payment-key --signing-key-file collat.xsk --out-file collat.skey
    rm collat.xsk
    ${cli} key verification-key --signing-key-file collat.skey --verification-key-file collat.vkey
    ${cli} address key-hash --payment-verification-key-file collat.vkey > collat.hash
    ${cli} address build --payment-verification-key-file collat.vkey ${network} --out-file collat.addr
    echo -e "\033[1;37m\nCollateral Address: $(cat collat.addr)\n\033[0m"
elif [[ "$input" == "2" ]]; then
    echo -e "\033[1;35m\nLoading Wallet...\n\033[0m"
    echo -e "\033[1;36m\nEnter The Seed Phrase\n\033[0m"

    read -r seed_phrase

    root=$(echo $seed_phrase | ${addr} key from-recovery-phrase Shelley)
    
    # batcher
    echo $root | ${addr} key child 1852H/1815H/0H/0/0 > batcher.xsk
    ${cli} key convert-cardano-address-key --shelley-payment-key --signing-key-file batcher.xsk --out-file batcher.skey
    rm batcher.xsk
    ${cli} key verification-key --signing-key-file batcher.skey --verification-key-file batcher.vkey
    ${cli} address key-hash --payment-verification-key-file batcher.vkey > batcher.hash
    ${cli} address build --payment-verification-key-file batcher.vkey ${network} --out-file batcher.addr
    echo -e "\033[1;37m\nBatcher Address: $(cat batcher.addr)\n\033[0m"
    
    # collateral
    echo $root | ${addr} key child 1852H/1815H/0H/0/1 > collat.xsk
    ${cli} key convert-cardano-address-key --shelley-payment-key --signing-key-file collat.xsk --out-file collat.skey
    rm collat.xsk
    ${cli} key verification-key --signing-key-file collat.skey --verification-key-file collat.vkey
    ${cli} address key-hash --payment-verification-key-file collat.vkey > collat.hash
    ${cli} address build --payment-verification-key-file collat.vkey ${network} --out-file collat.addr
    echo -e "\033[1;37m\nCollateral Address: $(cat collat.addr)\n\033[0m"

else
    echo "Exiting"
    exit 0;
fi

