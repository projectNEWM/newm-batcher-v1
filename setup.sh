#!/usr/bin/env bash

echo -e "\033[1;34m\nDownloading Required Binaries\n\033[0m"

if [ -x "bin/oura" ]; then
    echo -e "\033[1;31mOura Exists!\033[0m"
else
    wget -P bin https://github.com/txpipe/oura/releases/download/v1.9.1/oura-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf bin/oura-x86_64-unknown-linux-gnu.tar.gz -C bin --wildcards --no-anchored oura
    rm bin/oura-x86_64-unknown-linux-gnu.tar.gz
    ./bin/oura --version
fi

if [ -x "bin/ogmios" ]; then
    echo -e "\033[1;31mOgmios Exists!\033[0m"
else
    wget -P bin https://github.com/CardanoSolutions/ogmios/releases/download/v6.6.0/ogmios-v6.6.0-x86_64-linux.zip
    unzip -j bin/ogmios-v6.6.0-x86_64-linux.zip "bin/ogmios" -d bin
    rm bin/ogmios-v6.6.0-x86_64-linux.zip
    chmod +x bin/ogmios
    ./bin/ogmios --version
fi


if [ -x "bin/aiken" ]; then
    echo -e "\033[1;31mAiken Exists!\033[0m"
else
    wget -P bin https://github.com/aiken-lang/aiken/releases/download/v1.0.29-alpha/aiken-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf bin/aiken-x86_64-unknown-linux-gnu.tar.gz -C bin --strip-components=1 aiken-x86_64-unknown-linux-gnu/aiken
    rm bin/aiken-x86_64-unknown-linux-gnu.tar.gz
    ./bin/aiken --version
fi

if [ -x "bin/cardano-cli" ]; then
    echo -e "\033[1;31mCLI Exists!\033[0m"
else
    wget -P bin https://github.com/IntersectMBO/cardano-node/releases/download/9.1.0/cardano-node-9.1.0-linux.tar.gz
    tar -xzf bin/cardano-node-9.1.0-linux.tar.gz -C bin --strip-components=2 ./bin/cardano-cli
    rm bin/cardano-node-9.1.0-linux.tar.gz
    ./bin/cardano-cli --version
fi


