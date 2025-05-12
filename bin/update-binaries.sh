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
    wget -P . https://github.com/txpipe/oura/releases/download/v1.9.3/oura-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf ./oura-x86_64-unknown-linux-gnu.tar.gz -C . --wildcards --no-anchored oura
    rm ./oura-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mOura: $(./oura --version)\033[0m"
fi

if [ -x "./ogmios" ]; then
    echo -e "\033[1;31mOgmios Exists!\033[0m"
else
    wget -P . https://github.com/CardanoSolutions/ogmios/releases/download/v6.11.2/ogmios-v6.11.2-x86_64-linux.zip
    unzip -j ./ogmios-v6.11.2-x86_64-linux.zip "bin/ogmios" -d .
    rm ./ogmios-v6.11.2-x86_64-linux.zip
    chmod +x ./ogmios
    echo -e "\033[1;37mOgmios: $(./ogmios --version)\033[0m"
fi

if [ -x "./aiken" ]; then
    echo -e "\033[1;31mAiken Exists!\033[0m"
else
    wget -P . https://github.com/aiken-lang/aiken/releases/download/v1.1.17/aiken-x86_64-unknown-linux-musl.tar.gz
    tar -xzf ./aiken-x86_64-unknown-linux-musl.tar.gz -C . --strip-components=1 aiken-x86_64-unknown-linux-musl/aiken
    rm ./aiken-x86_64-unknown-linux-musl.tar.gz
    echo -e "\033[1;37mAiken: $(./aiken --version)\033[0m"
fi

if [ -x "./cardano-cli" ]; then
    echo -e "\033[1;31mCli Exists!\033[0m"
else
    wget -P . https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-10.8.0.0/cardano-cli-10.8.0.0-x86_64-linux.tar.gz
    tar -xzf ./cardano-cli-10.8.0.0-x86_64-linux.tar.gz -C .
    chmod +x ./cardano-cli-x86_64-linux
    mv ./cardano-cli-x86_64-linux ./cardano-cli
    rm ./cardano-cli-10.8.0.0-x86_64-linux.tar.gz
    echo -e "\033[1;37mCardano CLI: $(./cardano-cli --version)\033[0m"
fi

if [ -x "./cardano-address" ]; then
    echo -e "\033[1;31mAddr Exists!\033[0m"
else
    wget -P . https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-address-4.0.0-linux.tar.gz
    tar -xzf ./cardano-address-4.0.0-linux.tar.gz -C .
    rm ./cardano-address-4.0.0-linux.tar.gz
    chmod +x ./cardano-address
    echo -e "\033[1;37mCardano Address: $(./cardano-address --version)\033[0m"
fi