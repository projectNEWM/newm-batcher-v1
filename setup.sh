#!/usr/bin/env bash

echo -e "\033[1;34m\nDownloading Required Binaries\n\033[0m"

if [ -x "bin/cardano-cli" ]; then
    echo -e "\033[1;32mcardano-cli Exists!\033[0m"
else
    echo "The binary does not exist or is not executable."
fi
