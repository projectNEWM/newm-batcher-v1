#!/usr/bin/env bash

rm aiken || true
rm cardano-address || true
rm cardano-cli || true
rm ogmios || true
rm oura || true

echo -e "\033[1;34m\nDownloading Required Binaries\n\033[0m"

if [ -x "./oura" ]; then
    echo -e "\033[1;31mOura Exists!\033[0m"
else
    wget -P . https://github.com/txpipe/oura/releases/download/v1.9.2/oura-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf ./oura-x86_64-unknown-linux-gnu.tar.gz -C . --wildcards --no-anchored oura
    rm ./oura-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mOura: $(./oura --version)\033[0m"
fi

if [ -x "./ogmios" ]; then
    echo -e "\033[1;31mOgmios Exists!\033[0m"
else
    wget -P . https://github.com/CardanoSolutions/ogmios/releases/download/v6.10.0/ogmios-v6.10.0-x86_64-linux.zip
    unzip -j ./ogmios-v6.10.0-x86_64-linux.zip "bin/ogmios" -d .
    rm ./ogmios-v6.10.0-x86_64-linux.zip
    chmod +x ./ogmios
    echo -e "\033[1;37mOgmios: $(./ogmios --version)\033[0m"
fi

if [ -x "./aiken" ]; then
    echo -e "\033[1;31mAiken Exists!\033[0m"
else
    wget -P . https://github.com/aiken-lang/aiken/releases/download/v1.1.9/aiken-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf ./aiken-x86_64-unknown-linux-gnu.tar.gz -C . --strip-components=1 aiken-x86_64-unknown-linux-gnu/aiken
    rm ./aiken-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mAiken: $(./aiken --version)\033[0m"
fi

if [ -x "./cardano-cli" ]; then
    echo -e "\033[1;31mCli Exists!\033[0m"
else
    wget -P . https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-10.2.0.0/cardano-cli-10.2.0.0-x86_64-linux.tar.gz
    tar -xzf ./cardano-cli-10.2.0.0-x86_64-linux.tar.gz -C .
    chmod +x ./cardano-cli-x86_64-linux
    mv ./cardano-cli-x86_64-linux ./cardano-cli
    rm ./cardano-cli-10.2.0.0-x86_64-linux.tar.gz
    echo -e "\033[1;37mCardano CLI: $(./cardano-cli --version)\033[0m"
fi

if [ -x "./cardano-address" ]; then
    echo -e "\033[1;31mAddr Exists!\033[0m"
else
    wget -P . https://github.com/IntersectMBO/cardano-addresses/releases/download/3.12.0/cardano-addresses-3.12.0-linux64.tar.gz
    tar -xzf ./cardano-addresses-3.12.0-linux64.tar.gz -C . --strip-components=1 bin/cardano-address
    rm ./cardano-addresses-3.12.0-linux64.tar.gz
    chmod +x ./cardano-address
    echo -e "\033[1;37mCardano Address: $(./cardano-address --version)\033[0m"
fi