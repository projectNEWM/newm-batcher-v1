#!/usr/bin/env bash

###############################################################################
#########################           FUNCTION          #########################
###############################################################################

update_collat_utxo() {
    local yaml_file="config.yaml"  # Change this to your YAML file name

    network=$(yq '.network' config.yaml)
    cli=$(yq '.cli_path' config.yaml)
    socket_path=$(yq '.socket_path' config.yaml)

    echo
    echo -e "\033[1;36m\nSend Exactly 5 ADA To:\n\033[0m"
    echo -e "\033[1;37mCollateral Address: $(cat keys/collat.addr)\n\033[0m"

    # Loop until the node is connected
    while true; do
        utxo=$(${cli} conway query utxo --socket-path ${socket_path} --address $(cat keys/collat.addr) ${network} --output-json | jq -r 'to_entries[] | select(.value.value.lovelace == 5000000) | .key')

        # Check the result
        if [ -z "$utxo" ]; then
            echo "Waiting For Collateral Wallet To Be Funded..."
            sleep 5
        else
            echo "Collateral Is Ready"
            yq eval ".collat_utxo = \"$utxo\"" -i "$yaml_file"
            break
        fi
    done
    
}

update_profit_address() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    local address

    while true; do
        # Prompt for the address
        read -r -p "Enter the profit address: " address

        # Validate the address format (general regex for Cardano addresses)
        if [[ "$address" =~ ^(addr_test1|addr1)[0-9a-zA-Z]+$ ]]; then
            # Update the profit_address field in the YAML file
            yq eval ".profit_address = \"$address\"" -i "$yaml_file"
            echo "Updated profit_address to $address in $yaml_file"
            break  # Exit the loop
        else
            echo "Error: Invalid address format. Please ensure it starts with 'addr1' or 'addr_test1' and is followed by valid alphanumeric characters."
        fi
    done
}

create_wallet_keys() {
    local yaml_file="config.yaml"  # Change this to your YAML file name

    echo
    echo "Press 1 to generate a wallet, 2 to load a wallet"
    read -rsn1 input

    if [[ "$input" == "1" ]]; then
        echo -e "\033[1;35m\nGenerating Wallet...\n\033[0m"
        echo -e "\033[1;36m\nWrite Down These Words\n\033[0m"
        seed_phrase=$(${addr} recovery-phrase generate --size 24)
        echo $seed_phrase
        root=$(echo $seed_phrase | ${addr} key from-recovery-phrase Shelley)
        
        # batcher
        echo $root | ${addr} key child 1852H/1815H/0H/0/0 > keys/batcher.xsk
        ${cli} conway key convert-cardano-address-key --shelley-payment-key --signing-key-file keys/batcher.xsk --out-file keys/batcher.skey
        rm keys/batcher.xsk
        ${cli} conway key verification-key --signing-key-file keys/batcher.skey --verification-key-file keys/batcher.vkey
        ${cli} conway address key-hash --payment-verification-key-file keys/batcher.vkey > keys/batcher.hash
        ${cli} conway address build --payment-verification-key-file keys/batcher.vkey ${network} --out-file keys/batcher.addr
        echo -e "\033[1;37m\nBatcher Address: $(cat keys/batcher.addr)\n\033[0m"
        yq eval ".batcher_address = \"$(cat keys/batcher.addr)\"" -i "$yaml_file"
        
        # collateral
        echo $root | ${addr} key child 1852H/1815H/0H/0/1 > keys/collat.xsk
        ${cli} conway key convert-cardano-address-key --shelley-payment-key --signing-key-file keys/collat.xsk --out-file keys/collat.skey
        rm keys/collat.xsk
        ${cli} conway key verification-key --signing-key-file keys/collat.skey --verification-key-file keys/collat.vkey
        ${cli} conway address key-hash --payment-verification-key-file keys/collat.vkey > keys/collat.hash
        ${cli} conway address build --payment-verification-key-file keys/collat.vkey ${network} --out-file keys/collat.addr
        echo -e "\033[1;37m\nCollateral Address: $(cat keys/collat.addr)\n\033[0m"
        yq eval ".collat_address = \"$(cat keys/collat.addr)\"" -i "$yaml_file"


    elif [[ "$input" == "2" ]]; then
        echo -e "\033[1;35m\nLoading Wallet...\n\033[0m"
        echo -e "\033[1;36m\nEnter The Seed Phrase With A Single Space Between Each Word\n\033[0m"

        while true; do
            # Prompt for the seed phrase
            read -r -p "Seed Phrase: " seed_phrase

            # Run the command to get the root key in a subshell
            root=$(echo "$seed_phrase" | ${addr} key from-recovery-phrase Shelley 2>&1)
            exit_status=$?

            # Check if the command was successful
            if [ $exit_status -eq 0 ]; then
                echo "Root key: $root"
                break  # Exit the loop if successful
            else
                echo "Error: $root"  # Print the error message from the command
                echo "Please try again."
            fi
        done
        
        # batcher
        echo $root | ${addr} key child 1852H/1815H/0H/0/0 > keys/batcher.xsk
        ${cli} conway key convert-cardano-address-key --shelley-payment-key --signing-key-file keys/batcher.xsk --out-file keys/batcher.skey
        rm keys/batcher.xsk
        ${cli} conway key verification-key --signing-key-file keys/batcher.skey --verification-key-file keys/batcher.vkey
        ${cli} conway address key-hash --payment-verification-key-file keys/batcher.vkey > keys/batcher.hash
        ${cli} conway address build --payment-verification-key-file keys/batcher.vkey ${network} --out-file keys/batcher.addr
        echo -e "\033[1;37m\nBatcher Address: $(cat keys/batcher.addr)\n\033[0m"
        yq eval ".batcher_address = \"$(cat keys/batcher.addr)\"" -i "$yaml_file"

        
        # collateral
        echo $root | ${addr} key child 1852H/1815H/0H/0/1 > keys/collat.xsk
        ${cli} conway key convert-cardano-address-key --shelley-payment-key --signing-key-file keys/collat.xsk --out-file keys/collat.skey
        rm keys/collat.xsk
        ${cli} conway key verification-key --signing-key-file keys/collat.skey --verification-key-file keys/collat.vkey
        ${cli} conway address key-hash --payment-verification-key-file keys/collat.vkey > keys/collat.hash
        ${cli} conway address build --payment-verification-key-file keys/collat.vkey ${network} --out-file keys/collat.addr
        echo -e "\033[1;37m\nCollateral Address: $(cat keys/collat.addr)\n\033[0m"
        yq eval ".collat_address = \"$(cat keys/collat.addr)\"" -i "$yaml_file"


    else
        create_wallet_keys
    fi

}

update_file_paths() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    local directory
    local file1="config.json"  # Replace with the actual file name you're looking for
    local file2="node.socket"  # Replace with the actual file name you're looking for

    # Prompt user for directory
    echo
    read -e -p "Please enter the node directory where the files config.json and node.socket are located: " directory

    # Expand tilde to home directory
    directory="${directory/#\~/$HOME}"

    # Validate directory
    if [[ ! -d "$directory" ]]; then
        echo "Error: Directory does not exist."
        update_file_paths
        return
    fi

    # Find the files and get their absolute paths
    local file1_path
    local file2_path

    # file1_path=$(find "$directory" -type f -name "$file1" -print -quit)
    # file2_path=$(find "$directory" -type f -name "$file2" -print -quit)

    file1_path=$(find "$directory" -type f -name "$file1" 2>/dev/null)
    file2_path=$(find "$directory" -type s -name "$file2" 2>/dev/null)

    # Check if the files were found
    if [[ -z "$file1_path" ]]; then
        echo "Error: $file1 not found in the specified directory."
        update_file_paths
        return
    else
        file1_path=$(realpath "$file1_path")
        echo "Found $file1 at $file1_path"
    fi

    if [[ -z "$file2_path" ]]; then
        echo "Error: $file2 not found in the specified directory."
        # some nodes have it as socket
        file2_path=$(find "$directory" -type s -name "socket" 2>/dev/null)
            if [[ -z "$file2_path" ]]; then
            echo "Error: $file2 not found in the specified directory."
            update_file_paths
            return
        else
            file2_path=$(realpath "$file2_path")
            echo "Found $file2 at $file2_path"
        fi
    else
        file2_path=$(realpath "$file2_path")
        echo "Found $file2 at $file2_path"
    fi

    # Update the YAML file with the absolute paths
    yq eval ".node_config_path = \"$file1_path\" | .socket_path = \"$file2_path\"" -i "$yaml_file"
}

update_node_port() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    local node_port

    # Prompt for the node port
    echo
    read -p "What is the node port (1-65535)? " node_port

    # Check if the input is a valid integer and within the port range
    if ! [[ "$node_port" =~ ^[0-9]+$ ]] || [ "$node_port" -lt 1 ] || [ "$node_port" -gt 65535 ]; then
        echo "Error: Please enter a valid port number (1-65535)."
        # Call the function again to prompt the user
        update_node_port
        return
    fi

    # Update the node port in the YAML file
    yq eval ".node_port = $node_port" -i "$yaml_file"
    echo "Updated node_port to $node_port in $yaml_file"
}

update_use_ogmios() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    local use_ogmios

    # Prompt for using Ogmois or AIken
    echo
    read -p "Do you want to use Ogmois for Tx simulation? (yes/no) [No Uses Aiken] " use_ogmios

    # Validate input
    if [[ "$use_ogmios" == "yes" ]]; then
        yq eval ".use_ogmios = true" -i "$yaml_file"
    elif [[ "$use_ogmios" == "no" ]]; then
        yq eval ".use_ogmios = false" -i "$yaml_file"
    else
        echo "Error: Please enter 'yes' or 'no'."
        update_use_ogmios
        return
    fi

    echo "Updated use_ogmios to $use_ogmios in $yaml_file"
}

update_network() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    local network

    # Prompt for using Mainnet or Testnet
    echo
    read -p "Is this on Mainnet or Testnet? (mainnet/testnet) [Testnet Is Pre-Production] " network

    # Validate input
    if [[ "$network" == "mainnet" ]]; then
        yq eval ".network = \"--mainnet\"" -i "$yaml_file"
    elif [[ "$network" == "testnet" ]]; then
        yq eval ".network = \"--testnet-magic 1\"" -i "$yaml_file"
    else
        echo "Error: Please enter 'mainnet' or 'testnet'."
        update_network
        return
    fi

    echo "Updated network to $network in $yaml_file"
}

update_bin_paths() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    yq eval ".aiken_path = \"$(realpath "$(pwd)/bin/aiken")\"" -i "$yaml_file" 
    yq eval ".addr_path = \"$(realpath "$(pwd)/bin/cardano-address")\"" -i "$yaml_file" 
    yq eval ".cli_path = \"$(realpath "$(pwd)/bin/cardano-cli")\"" -i "$yaml_file" 
    yq eval ".ogmios_path = \"$(realpath "$(pwd)/bin/ogmios")\"" -i "$yaml_file" 
    yq eval ".oura_path = \"$(realpath "$(pwd)/bin/oura")\"" -i "$yaml_file" 
}


###############################################################################
clear
echo
echo /
echo //
echo ///
echo ////
printf "%s" $(echo "NEWM-Batcher-V1:" | fold -w1  | awk '{ printf "\033[1;%dm%s", 31+int(rand()*6), $1 }' | tr -d '\n') && echo -ne "\033[0m"
echo -e "\033[3;37m The NEWM Marketplace Order Batcher!\033[0m"
echo ////
echo ///
echo //
echo /
echo


echo -e "\033[5;37m\nPress Enter To Setup The NEWM Batcher, Or Any Other Key To Exit.\n\033[0m"
read -rsn1 input

if [[ "$input" == "" ]]; then
    echo -e "\033[37;33m\nContinuing...\n\033[0m"
    # Add your code here that should execute if Enter is pressed
else
    clear
    exit 0
fi

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
    echo -e "\033[1;33m sudo apt install -y python3 \033[0m"
    exit 1;
fi

if dpkg -s python3-venv &> /dev/null; then
    echo -e "\033[1;35m\npython3-venv is installed.\n\033[0m"
else
    echo -e "\033[1;31mpython3-venv is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y python3-venv \033[0m"
    exit 1;
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
    wget -P bin https://github.com/CardanoSolutions/ogmios/releases/download/v6.6.2/ogmios-v6.6.2-x86_64-linux.zip
    unzip -j bin/ogmios-v6.6.2-x86_64-linux.zip "bin/ogmios" -d bin
    rm bin/ogmios-v6.6.2-x86_64-linux.zip
    chmod +x bin/ogmios
    echo -e "\033[1;37mOgmios: $(./bin/ogmios --version)\033[0m"
fi


if [ -x "bin/aiken" ]; then
    echo -e "\033[1;31mAiken Exists!\033[0m"
else
    wget -P bin https://github.com/aiken-lang/aiken/releases/download/v1.1.3/aiken-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf bin/aiken-x86_64-unknown-linux-gnu.tar.gz -C bin --strip-components=1 aiken-x86_64-unknown-linux-gnu/aiken
    rm bin/aiken-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mAiken: $(./bin/aiken --version)\033[0m"

fi

if [ -x "bin/cardano-cli" ]; then
    echo -e "\033[1;31mCli Exists!\033[0m"
else
    wget -P bin https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-9.4.1.0/cardano-cli-9.4.1.0-x86_64-linux.tar.gz
    tar -xzf bin/cardano-cli-9.4.1.0-x86_64-linux.tar.gz -C bin
    chmod +x bin/cardano-cli-x86_64-linux
    mv bin/cardano-cli-x86_64-linux ./bin/cardano-cli
    rm bin/cardano-cli-9.4.1.0-x86_64-linux.tar.gz
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

update_network
update_use_ogmios
update_node_port
update_file_paths
update_bin_paths

echo -e "\033[1;36m\nCreating The Batcher and Collateral Keys Then Update The config.yaml File\n\033[0m"
echo -e "\033[31;33mChecking For Live Cardano Node...\n\033[0m"

./check_cardano_node.sh

exit_status=$?

# Check the exit status
if [ $exit_status -eq 1 ]; then
    exit 1;
fi

network=$(yq '.network' config.yaml)
cli=$(yq '.cli_path' config.yaml)
addr=$(yq '.addr_path' config.yaml)
socket_path=$(yq '.socket_path' config.yaml)

if [ -e "keys/batcher.skey" ] || [ -e "keys/collat.skey" ]; then
    echo -e "\033[1;31m\nKeys Exists\n\033[0m"
else
    create_wallet_keys
fi

update_profit_address

update_collat_utxo