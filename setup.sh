#!/usr/bin/env bash

###############################################################################
#########################           FUNCTION          #########################
###############################################################################

confirm_batcher_readiness() {
    echo
    echo -e "\033[1;37mChecking If Batcher Is Ready\n\033[0m"

    network=$(yq '.network' config.yaml)
    cli=$(yq '.cli_path' config.yaml)
    socket_path=$(yq '.socket_path' config.yaml)
    batcher_address=$(cat keys/batcher.addr)
    batcher_policy=$(yq '.batcher_policy' config.yaml)

    while true; do
        # Execute the query and get the length of the result
        result=$(${cli} conway query utxo --socket-path ${socket_path} --address ${batcher_address} ${network} --output-json |  jq --arg pid "${batcher_policy}" -r 'to_entries[] | if .value.value[$pid] != null then true else false end')

        if [ "$result" = "true" ]; then
            echo "Batcher Is Ready"
            break
        else
            echo "Transaction Pending. Sleeping for 10 seconds..."
            sleep 10
        fi
    done
}

create_vault_and_cert() {
    local batcher_utxo=$1  # Assign the first argument to a local variable
    local batcher_assets=$2  # Assign the first argument to a local variable
    echo "Batcher UTxO: $batcher_utxo"
    # echo "Batcher Assets: $batcher_assets"

    batcher_address=$(cat keys/batcher.addr)
    batcher_pkh=$(cat keys/batcher.hash)
    collat_pkh=$(cat keys/collat.hash)
    collat_utxo=$(yq '.collat_utxo' config.yaml)

    profit_address=$(yq '.profit_address' config.yaml)

    jq --arg var "${batcher_pkh}" '.fields[0].bytes=$var' tmp/wallet-datum.json | sponge tmp/wallet-datum.json

    # visually confirm the datum
    echo -e "\033[1;37m\nDoes the Batcher Hash Match?\n\033[0m"
    echo -e "\033[1;36m$(cat keys/batcher.hash)\n\033[0m"
    cat tmp/wallet-datum.json | jq
    echo -e "\033[1;31m\nThe Hashes Must Match\n\033[0m"

    echo -e "\033[5;37m\nPress Enter To Confirm The Hashes, Or Any Other Key To Exit.\n\033[0m"
    read -rsn1 input

    if [[ "$input" == "" ]]; then
        echo -e "\033[37;33m\nContinuing...\n\033[0m"
        # Add your code here that should execute if Enter is pressed
    else
        exit 0
    fi

    network=$(yq '.network' config.yaml)
    cli=$(yq '.cli_path' config.yaml)
    socket_path=$(yq '.socket_path' config.yaml)

    vault_address=$(yq '.vault_address' config.yaml)
    band_address=$(yq '.band_address' config.yaml)

    assets=$(python3 -c "from src.utility import generate_token_string; assets = generate_token_string(${batcher_assets});print(assets);")
    min_utxo=$(${cli} conway transaction calculate-min-required-utxo \
        --protocol-params-file tmp/protocol.json \
        --tx-out-inline-datum-file tmp/wallet-datum.json \
        --tx-out="${band_address} + 5000000 + ${assets}" | tr -dc '0-9')

    vault_address_output="${vault_address} + 10000000"
    band_address_output="${band_address} + ${min_utxo} + ${assets}"

    # create two vault utxos and send the back into the band contract
    echo -e "\033[0;36m Building Tx \033[0m"
    FEE=$(${cli} conway transaction build \
        --socket-path ${socket_path} \
        --out-file tmp/tx.draft \
        --tx-in ${batcher_utxo} \
        --change-address ${batcher_address} \
        --tx-out="${vault_address_output}" \
        --tx-out-inline-datum-file tmp/wallet-datum.json  \
        --tx-out="${vault_address_output}" \
        --tx-out-inline-datum-file tmp/wallet-datum.json  \
        --tx-out="${band_address_output}" \
        --tx-out-inline-datum-file tmp/wallet-datum.json  \
    ${network})

    IFS=':' read -ra VALUE <<< "${FEE}"
    IFS=' ' read -ra FEE <<< "${VALUE[1]}"
    echo -e "\033[1;32m Fee:\033[0m" $FEE

    echo -e "\033[0;36m Signing \033[0m"
    ${cli} conway transaction sign \
        --signing-key-file keys/batcher.skey \
        --tx-body-file tmp/tx.draft \
        --out-file tmp/tx.signed \
        ${network}
    
    echo -e "\033[0;36m Submitting \033[0m"
    ${cli} conway transaction submit \
        --socket-path ${socket_path} \
        ${network} \
        --tx-file tmp/tx.signed
    
    txid=$(${cli} conway transaction txid --tx-body-file tmp/tx.draft)

    while true; do
        # Execute the query and get the length of the result
        len=$(${cli} conway query utxo --socket-path ${socket_path} --tx-in ${txid}#0 ${network} --output-json | jq 'length')

        if [ "$len" -eq 0 ]; then
            echo "Transaction Pending. Sleeping for 10 seconds..."
            sleep 10
        else
            echo "UTXO found!"
            break  # Exit the loop when a non-zero length is found
        fi
    done

    batcher_utxo=${txid}#3
    band_utxo=${txid}#2

    IFS='#' read -ra array <<< "${band_utxo}"

    batcher_token_prefix="affab1e0005e77ab1e"
    complete_token_prefix="c011ec7ed000a55e75"
    batcher_policy=$(yq '.batcher_policy' config.yaml)
    batcher_token_name=$(python3 -c "from src.utility import generate_token_name; tkn=generate_token_name('${array[0]}', ${array[1]}, '${batcher_token_prefix}'); print(tkn)")
    complete_token_name=$(python3 -c "from src.utility import generate_token_name; tkn=generate_token_name('${array[0]}', ${array[1]}, '${complete_token_prefix}'); print(tkn)")

    complete_token="1 ${batcher_policy}.${complete_token_name}"

    batcher_token="1 ${batcher_policy}.${batcher_token_name}"

    min_utxo=$(${cli} conway transaction calculate-min-required-utxo \
        --protocol-params-file tmp/protocol.json \
        --tx-out-inline-datum-file tmp/wallet-datum.json \
        --tx-out="${band_address} + 5000000 + ${assets} + ${complete_token}" | tr -dc '0-9')

    band_address_output="${band_address} + ${min_utxo} + ${assets} + ${complete_token}"
    batcher_address_out="${batcher_address} + 5000000 + ${batcher_token}"

    band_ref_utxo=$(yq '.band_ref_utxo' config.yaml)
    batcher_ref_utxo=$(yq '.batcher_ref_utxo' config.yaml)

    data_address=$(yq '.data_address' config.yaml)
    data_policy=$(yq '.data_policy' config.yaml)
    data_asset=$(yq '.data_asset' config.yaml)
    data_ref_utxo=$(${cli} conway query utxo --socket-path ${socket_path} --address ${data_address} ${network} --output-json | jq --arg pid "${data_policy}"  --arg tkn "${data_asset}" -r 'to_entries[] | select(.value.value[$pid][$tkn] == 1) | .key' )

    cp batcher_token.cbor.hex metadata.hex
    sed -i "s/policy_here000000000000000000000000000000000000000000000/$batcher_policy/g" metadata.hex
    sed -i "s/affab1e000000000000000000000000000000000000000000000000000000000/$batcher_token_name/g" metadata.hex
    xxd -r -p metadata.hex > batcher_token.cbor

    echo -e "\033[0;36m Building Tx \033[0m"
    FEE=$(${cli} conway transaction build \
        --socket-path ${socket_path} \
        --out-file tmp/tx.draft \
        --change-address ${profit_address} \
        --read-only-tx-in-reference="${data_ref_utxo}" \
        --tx-in-collateral="${collat_utxo}" \
        --tx-in ${batcher_utxo} \
        --tx-in ${band_utxo} \
        --spending-tx-in-reference="${band_ref_utxo}" \
        --spending-plutus-script-v3 \
        --spending-reference-tx-in-inline-datum-present \
        --spending-reference-tx-in-redeemer-file tmp/mint-band-redeemer.json \
        --tx-out="${batcher_address_out}" \
        --tx-out="${band_address_output}" \
        --tx-out-inline-datum-file tmp/wallet-datum.json  \
        --required-signer-hash ${batcher_pkh} \
        --required-signer-hash ${collat_pkh} \
        --mint="${batcher_token} + ${complete_token}" \
        --mint-tx-in-reference="${batcher_ref_utxo}" \
        --mint-plutus-script-v3 \
        --policy-id="${batcher_policy}" \
        --mint-reference-tx-in-redeemer-file tmp/mint-batcher-redeemer.json \
        --metadata-cbor-file batcher_token.cbor \
        ${network})

    IFS=':' read -ra VALUE <<< "${FEE}"
    IFS=' ' read -ra FEE <<< "${VALUE[1]}"
    echo -e "\033[1;32m Fee:\033[0m" $FEE

    echo -e "\033[0;36m Signing \033[0m"
    ${cli} conway transaction sign \
        --signing-key-file keys/batcher.skey \
        --signing-key-file keys/collat.skey \
        --tx-body-file tmp/tx.draft \
        --out-file tmp/tx.signed \
        ${network}
    
    echo -e "\033[0;36m Submitting \033[0m"
    ${cli} conway transaction submit \
        --socket-path ${socket_path} \
        ${network} \
        --tx-file tmp/tx.signed
}

get_batcher_utxo() {
    echo
    echo -e "\033[1;36m\nSend Exactly 50 ADA And Band Tokens To:\n\033[0m"
    echo -e "\033[1;37mBatcher Address: $(cat keys/batcher.addr)\n\033[0m"

    network=$(yq '.network' config.yaml)
    cli=$(yq '.cli_path' config.yaml)
    socket_path=$(yq '.socket_path' config.yaml)

    # Loop until the node is connected
    while true; do
        utxo=$(${cli} conway query utxo --socket-path ${socket_path} --address $(cat keys/batcher.addr) ${network} --output-json | jq -r 'to_entries[] | select(.value.value.lovelace == 50000000) | .key' )
        assets=$(${cli} conway query utxo --socket-path ${socket_path} --address $(cat keys/batcher.addr) ${network} --output-json | jq -c 'to_entries[] | .value.value')
        
        # Check the result
        if [ -z "$utxo" ]; then
            echo "Waiting For Batcher Wallet To Be Funded..."
            sleep 10
        else
            echo "Creating Vault UTxOs and Minting Certificate Token"
            # run the tx scripts here
            create_vault_and_cert $utxo $assets
            break
        fi
    done


}

update_collat_utxo() {
    local yaml_file="config.yaml"  # Change this to your YAML file name

    network=$(yq '.network' config.yaml)
    cli=$(yq '.cli_path' config.yaml)
    socket_path=$(yq '.socket_path' config.yaml)

    utxo=$(${cli} conway query utxo --socket-path ${socket_path} --address $(cat keys/collat.addr) ${network} --output-json | jq -r 'to_entries[] | select(.value.value.lovelace == 5000000) | .key')
    # Check the result
    if [ -z "$utxo" ]; then
        sleep 1
    else
        echo -e "\033[1;37mCollateral Is Ready\033[0m"
        yq eval ".collat_utxo = \"$utxo\"" -i "$yaml_file"
        yq eval ".collat_address = \"$(cat keys/collat.addr)\"" -i "$yaml_file"
        return
    fi
    echo
    echo -e "\033[1;36m\nSend Exactly 5 ADA To:\n\033[0m"
    echo -e "\033[1;37mCollateral Address: $(cat keys/collat.addr)\n\033[0m"

    # Loop until the node is connected
    while true; do
        utxo=$(${cli} conway query utxo --socket-path ${socket_path} --address $(cat keys/collat.addr) ${network} --output-json | jq -r 'to_entries[] | select(.value.value.lovelace == 5000000) | .key')

        # Check the result
        if [ -z "$utxo" ]; then
            echo "Waiting For Collateral Wallet To Be Funded..."
            sleep 10
        else
            echo "Collateral Is Ready"
            yq eval ".collat_utxo = \"$utxo\"" -i "$yaml_file"
            yq eval ".collat_address = \"$(cat keys/collat.addr)\"" -i "$yaml_file"
            break
        fi
    done
    
}

update_profit_address() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    local address
    
    while true; do
        # Prompt for the address
        echo
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

        echo -e "\033[1;37m\nPress Enter To Continue, Or Any Other Key To Exit.\n\033[0m"
        read -rsn1 input

        if [[ "$input" == "" ]]; then
            echo -e "\033[37;33m\nContinuing...\n\033[0m"
            # Add your code here that should execute if Enter is pressed
        else
            clear
            exit 1
        fi

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
    read -e -p "Please enter the parent directory where the node config.json and node.socket files are located: " directory

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

    file1_path=$(find "$directory" -type f -name "$file1" -print -quit)
    file2_path=$(find "$directory" -type s -name "$file2" -print -quit)

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
    read -p "What is the Cardano node port (1-65535)? " node_port

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
    read -p "Do you want to use Ogmois for tx simulation? (yes/no) [No Uses Aiken] " use_ogmios

    # Validate input
    if [[ "$use_ogmios" == "yes" ]]; then
        yq eval ".use_ogmios = true" -i "$yaml_file"
        echo "Updated use_ogmios to true in $yaml_file"
    elif [[ "$use_ogmios" == "no" ]]; then
        yq eval ".use_ogmios = false" -i "$yaml_file"
        echo "Updated use_ogmios to false in $yaml_file"
    else
        echo "Error: Please enter 'yes' or 'no'."
        update_use_ogmios
        return
    fi
}

update_network() {
    local yaml_file="config.yaml"  # Change this to your YAML file name
    local network

    # Prompt for using Mainnet or Testnet
    echo
    read -p "Is this on mainnet or testnet? (mainnet/testnet) [Testnet Is Pre-Production] " network

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

sleep 1
clear
if [[ "$input" == "" ]]; then
    echo -e "\033[37;33m\nContinuing...\n\033[0m"
    # Add your code here that should execute if Enter is pressed
else
    exit 0
fi

###############################################################################
###############################################################################
###############################################################################

echo -e "\033[1;34m\nChecking For Required Binaries\n\033[0m"

# Check if running on Linux
if [[ "$(uname -s)" == "Linux" ]]; then
    echo -e "\033[1;33m\nRunning on Linux. Proceeding...\n\033[0m"
else
    echo -e "\033[1;31m\nOnly Linux Is Supported. Exiting script.\n\033[0m"
    exit 1;
fi

if command -v sed &> /dev/null; then 
    echo -e "\033[1;35m\nsed is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31msed is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y sed \033[0m"
    exit 1;
fi

if command -v xxd &> /dev/null; then 
    echo -e "\033[1;35m\nxxd is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31mxxd is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y xxd \033[0m"
    exit 1;
fi

if command -v sponge &> /dev/null; then
    echo -e "\033[1;35m\nsponge is installed and available on the PATH.\n\033[0m"
else
    echo -e "\033[1;31msponge is not installed or not available on the PATH.\033[0m"
    echo -e "\033[1;33m sudo apt install -y moreutils \033[0m"
    exit 1;
fi

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
    echo -e "\033[1;33m sudo wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq && sudo chmod +x /usr/bin/yq \033[0m"
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
echo -e "\033[1;34m\nBinaries Are Ready\n\033[0m"

###############################################################################
###############################################################################
###############################################################################

sleep 1
clear
echo -e "\033[1;34m\nSetup Virtual Environment\n\033[0m"
# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt --progress-bar=on
echo -e "\033[1;34m\nVirtual Environment Is Ready\n\033[0m"

###############################################################################
###############################################################################
###############################################################################

sleep 1
clear
echo -e "\033[1;34m\nDownloading Required Binaries\n\033[0m"

if [ -x "bin/oura" ]; then
    echo -e "\033[1;31mOura Exists!\033[0m"
else
    wget -P bin https://github.com/txpipe/oura/releases/download/v1.9.3/oura-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf bin/oura-x86_64-unknown-linux-gnu.tar.gz -C bin --wildcards --no-anchored oura
    rm bin/oura-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mOura: $(./bin/oura --version)\033[0m"
fi

if [ -x "bin/ogmios" ]; then
    echo -e "\033[1;31mOgmios Exists!\033[0m"
else
    wget -P bin https://github.com/CardanoSolutions/ogmios/releases/download/v6.11.2/ogmios-v6.11.2-x86_64-linux.zip
    unzip -j bin/ogmios-v6.11.2-x86_64-linux.zip "bin/ogmios" -d bin
    rm bin/ogmios-v6.11.2-x86_64-linux.zip
    chmod +x bin/ogmios
    echo -e "\033[1;37mOgmios: $(./bin/ogmios --version)\033[0m"
fi

if [ -x "bin/aiken" ]; then
    echo -e "\033[1;31mAiken Exists!\033[0m"
else
    wget -P bin https://github.com/aiken-lang/aiken/releases/download/v1.1.17/aiken-x86_64-unknown-linux-gnu.tar.gz
    tar -xzf bin/aiken-x86_64-unknown-linux-gnu.tar.gz -C bin --strip-components=1 aiken-x86_64-unknown-linux-gnu/aiken
    rm bin/aiken-x86_64-unknown-linux-gnu.tar.gz
    echo -e "\033[1;37mAiken: $(./bin/aiken --version)\033[0m"
fi

if [ -x "bin/cardano-cli" ]; then
    echo -e "\033[1;31mCli Exists!\033[0m"
else
    wget -P bin https://github.com/IntersectMBO/cardano-cli/releases/download/cardano-cli-10.8.0.0/cardano-cli-10.8.0.0-x86_64-linux.tar.gz
    tar -xzf bin/cardano-cli-10.8.0.0-x86_64-linux.tar.gz -C bin
    chmod +x bin/cardano-cli-x86_64-linux
    mv bin/cardano-cli-x86_64-linux ./bin/cardano-cli
    rm bin/cardano-cli-10.8.0.0-x86_64-linux.tar.gz
    echo -e "\033[1;37mCardano CLI: $(./bin/cardano-cli --version)\033[0m"
fi

if [ -x "bin/cardano-address" ]; then
    echo -e "\033[1;31mAddr Exists!\033[0m"
else
    wget -P bin https://github.com/IntersectMBO/cardano-addresses/releases/download/4.0.0/cardano-addresses-4.0.0-linux64.tar.gz
    tar -xzf bin/cardano-addresses-4.0.0-linux64.tar.gz -C bin --strip-components=1 bin/cardano-address
    rm bin/cardano-addresses-4.0.0-linux64.tar.gz
    chmod +x bin/cardano-address
    echo -e "\033[1;37mCardano Address: $(./bin/cardano-address --version)\033[0m"
fi

###############################################################################
###############################################################################
###############################################################################

sleep 1
clear
echo -e "\033[1;34m\nSetup The Configuration\n\033[0m"

update_network
update_use_ogmios
update_node_port
update_file_paths
update_bin_paths
update_profit_address

echo -e "\033[1;34m\nConfiguration Is Ready\n\033[0m"

###############################################################################
###############################################################################
###############################################################################

sleep 1
clear
echo -e "\033[1;36m\nCreating The Batcher and Collateral Keys\n\033[0m"
echo -e "\033[5;33mChecking For Live Cardano Node...\n\033[0m"

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
    echo -e "\033[1;37m\nKeys Exists\n\033[0m"
else
    create_wallet_keys
fi

sleep 1
clear
echo -e "\033[1;31m\nEach Wallet Requires A Single UTxO Only\033[0m"
echo -e "\033[1;31mBe Patient And Follow Directions\n\033[0m"

update_collat_utxo

batcher_address=$(cat keys/batcher.addr)
batcher_policy=$(yq '.batcher_policy' config.yaml)
result=$(${cli} conway query utxo --socket-path ${socket_path} --address ${batcher_address} ${network} --output-json |  jq --arg pid "${batcher_policy}" -r 'to_entries[] | if .value.value[$pid] != null then true else false end')

if [ "$result" = "true" ]; then
    yq eval ".batcher_address = \"$(cat keys/batcher.addr)\"" -i "config.yaml"
    echo -e "\033[1;37mBatcher Is Ready\033[0m"
else
    get_batcher_utxo
    confirm_batcher_readiness
fi

sleep 1
clear
echo
echo /
echo //
echo ///
echo ////
printf "%s" $(echo "Enjoy" | fold -w1  | awk '{ printf "\033[1;%dm%s", 31+int(rand()*6), $1 }' | tr -d '\n') && echo -ne "\033[0m"
echo -e "\033[3;37m The NEWM Marketplace Order Batcher!\033[0m"
echo ////
echo ///
echo //
echo /
echo
