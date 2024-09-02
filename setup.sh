#!/usr/bin/env bash

# Check if running on Linux
if [[ "$(uname -s)" == "Linux" ]]; then
    echo -e "\033[1;33m\nRunning on Linux. Proceeding...\n\033[0m"
else
    echo -e "\033[1;31m\nOnly Linux Is Supported. Exiting script.\n\033[0m"
    exit 1;
fi

echo -e "\033[1;34m\nChecking For Required Binaries\n\033[0m"

if command -v git &> /dev/null; then
    echo -e "\033[1;35m\ngit is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31mgit is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y git \033[0m"
    exit 1;
fi

if command -v tar &> /dev/null; then
    echo -e "\033[1;35m\ntar is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31mtar is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y tar \033[0m"
    exit 1;
fi

if command -v zip &> /dev/null; then
    echo -e "\033[1;35m\nzip is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31mzip is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y zip unzip \033[0m"
    exit 1;
fi

if command -v wget &> /dev/null; then
    echo -e "\033[1;35m\nwget is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31mwget is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y wget \033[0m"
    exit 1;
fi

if command -v jq &> /dev/null; then
    echo -e "\033[1;35m\njq is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31mjq is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y jq \033[0m"
    exit 1;
fi

if command -v yq &> /dev/null; then
    echo -e "\033[1;35m\nyq is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31myq is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \033[0m"
    echo -e "\033[1;33m sudo chmod a+x /usr/local/bin/yq \033[0m"
    exit 1;
fi

if command -v python3 &> /dev/null; then
    echo -e "\033[1;35m\npython3 is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31mpython3 is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y python3 python3-venv \033[0m"
    exit 1;
fi

if dpkg -s python3-venv &> /dev/null; then
    echo -e "\033[1;35m\npython3-venv is installed.\n\033[0m"
else
    echo -e "\033[1;31mpython3-venv is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y python3-venv \033[0m"
fi

echo -e "\033[1;34m\nSetup Virtual Environment\n\033[0m"

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

echo -e "\033[1;34m\nDownloading Required Binaries\n\033[0m"

if [ -x "bin/oura" ]; then
    echo -e "\033[1;31mOura Exists!\033[0m"
else
    wget -P bin https://github.com/txpipe/oura/releases/download/v1.9.1/oura-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf bin/oura-x86_64-unknown-linux-gnu.tar.gz -C bin --wildcards --no-anchored oura
    rm bin/oura-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mOura: $(./bin/oura --version)\033[0m"
fi

if [ -x "bin/ogmios" ]; then
    echo -e "\033[1;31mOgmios Exists!\033[0m"
else
    wget -P bin https://github.com/CardanoSolutions/ogmios/releases/download/v6.6.0/ogmios-v6.6.0-x86_64-linux.zip
    unzip -j bin/ogmios-v6.6.0-x86_64-linux.zip "bin/ogmios" -d bin
    rm bin/ogmios-v6.6.0-x86_64-linux.zip
    chmod +x bin/ogmios
    echo -e "\033[1;37mOgmios: $(./bin/ogmios --version)\033[0m"
fi


if [ -x "bin/aiken" ]; then
    echo -e "\033[1;31mAiken Exists!\033[0m"
else
    wget -P bin https://github.com/aiken-lang/aiken/releases/download/v1.0.29-alpha/aiken-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf bin/aiken-x86_64-unknown-linux-gnu.tar.gz -C bin --strip-components=1 aiken-x86_64-unknown-linux-gnu/aiken
    rm bin/aiken-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mAiken: $(./bin/aiken --version)\033[0m"

fi

if [ -x "bin/cardano-cli" ]; then
    echo -e "\033[1;31mCli Exists!\033[0m"
else
    wget -P bin https://github.com/IntersectMBO/cardano-node/releases/download/9.1.0/cardano-node-9.1.0-linux.tar.gz
    tar -xzf bin/cardano-node-9.1.0-linux.tar.gz -C bin --strip-components=2 ./bin/cardano-cli
    rm bin/cardano-node-9.1.0-linux.tar.gz
    echo -e "\033[1;37mCardano CLI: $(./bin/cardano-cli --version)\033[0m"
fi

if [ -x "bin/cardano-address" ]; then
    echo -e "\033[1;31mAddr Exists!\033[0m"
else
    wget -P bin https://github.com/IntersectMBO/cardano-addresses/releases/download/3.12.0/cardano-addresses-3.12.0-linux64.tar.gz
    tar -xzf bin/cardano-addresses-3.12.0-linux64.tar.gz -C bin --strip-components=1 bin/cardano-address
    rm bin/cardano-addresses-3.12.0-linux64.tar.gz
    chmod +x bin/cardano-address
    echo -e "\033[1;37mCardano Address: $(./bin/cardano-address --version)\033[0m"
fi

echo -e "\033[1;36m\nCreate The Batcher and Collateral Keys Then Update The config.yaml File\n\033[0m"
