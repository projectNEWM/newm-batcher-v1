# NEWM Market Batcher v1

This is the first version of the [NEWM Marketplace](https://github.com/projectNEWM/newm-market) order batcher. This lightweight tool processes orders using the sale and query contracts, prioritizing queue entries with larger incentives. It features automatic profit accumulation, multi-asset incentive list, and arbitrary transaction simulation. Fulfilling orders with the batcher requires a batcher certificate, obtained by locking a complete NEWM Monster set into the band-lock-up contract in the marketplace. The batcher is designed to run alongside a fully-synced node.

## Batcher Setup

Clone the repo and create your own personal branch for the batcher.

```bash
git clone https://github.com/newm-batcher-v1.git
cd newm-batcher-v1
git checkout -b your-personal-branch
```

The batcher requires a fully-synced cardano node and requires cardano-cli, cardano-address, [Ogmios](https://github.com/CardanoSolutions/ogmios), [Oura](https://github.com/txpipe/oura), [Aiken](https://github.com/aiken-lang/aiken), python3, yq, and jq.

The batcher comes with a setup helper file, `setup.sh`. This file will check and download all required external binaries. It will create the python virtual environment and install the required modules. It is assumed the cardano-node is already running and is fully-synced.

After the setup is completed, create the batcher and collateral keys using the `keys/setup_keys.sh` script then update the `config.yaml` file.

### Required CLI Keys

The batcher comes with a wallet setup helper file, `setup_keys.sh`, inside the `keys` folder that will allow the batcher to use a CIP03 wallet to generate the required cardano-cli keys. The script will prompt the user with the message below.

```
Press 1 to generate a wallet, 2 to load a wallet, or any other key to exit.
```

If the user wishes to generate a wallet then press 1. It will display a seed phrase for the user to write down then it will generate the required keys. If the user wishes to use an existing wallet then press 2. It will prompt the user to type in there seed phrase in a single line with single spaces between each word. If entered correctly then the script will generate the required keys. Any other key will exit the script. The script is designed to prevent overwriting.

After successfully setting up the wallet, the keys folder will contain two sets of files, one for the batcher and the other for the collateral, corresponding to the zeroth and first key paths from the root key.

```bash
# batcher keys
batcher.addr
batcher.hash
batcher.skey
batcher.vkey
# collateral keys
collat.addr
collat.hash
collat.skey
collat.vkey
```

The batcher address will hold a single UTxO with the batcher certificate token and 5 ADA. The collateral address will hold a single UTxO with 5 ADA. The balances of these addresses can be view with the `balances.sh` script located in the `keys` folder as well as with the `analysis.py` file in the parent directory using the `python3 analysis.py --batcher` command.

Using the setup script is not required as any valid cli keys can be used for the batcher. It is provided as a way to help secure the keys incase of failure or emergency.

### Obtaining A Batcher Certificate

A batcher certificate is issued when a user obtains a complete set of NEWM monsters and locks the entire band into a contract. The locking transaction mints a complete assets token that lives on the band lock UTxO and mints one batcher certificate to the user. The batcher certificate is sellable and tradable. It can be burned at any time to unlock the NEWM monsters that created it but can only unlock with the matching completed assets token. This perserves ownership even after trading.

After minting a batcher certificate, send the token with at least 5 ADA to the batcher address. A batcher will be unable to batch without the token.

Please refer to the [NEWM Marketplace Documentation](https://github.com/projectNEWM/newm-market/blob/master/README.md) about minting a batcher certificate token.

### Configuration

The `config.yaml` file is split into two parts. The user is expected to update just the top part that states `# Update Values For Your Batcher`. Configuring the batcher is placing the correct information into the fields below. The other information inside the `config.yaml` file does not need to be changed nor updated.

```yaml
# Batcher Information
batcher_address: ""
profit_address: ""

# Collat Wallet Information
collat_address: ""
collat_utxo: ""

# Network Information
network: "--testnet-magic 1"

# Bin Paths; Need To be Absolute
cli_path: "/newm-batcher-v1/bin/cardano-cli"
oura_path: "/newm-batcher-v1/bin/oura"
ogmios_path: "/newm-batcher-v1/bin/ogmios"
aiken_path: "/newm-batcher-v1/bin/aiken"
addr_path: "/newm-batcher-v1/bin/cardano-address"

# File Paths; Needs To Be Absolute
socket_path: "/node.socket"
node_config_path: "/config.json"
```

Replace the `batcher_address` with value from the batcher.addr file and `collat_address` with value from the collat.addr. The profit address can be another base address from the CIP03 wallet or any address of your choosing. The `collat_utxo` has the form `id#idx` and it holds 5 ADA. It will be used in every smart contract transaction as the collateral. The batcher is designed to run pre-production only. The required paths need to be absolute and complete.

The batcher is ready to run after this information has been updated. Do not update any other variables as it may inhibit the batcher's ability to function.

### Setting Up The Vaults

The final step for the batcher requires creating vault UTxOs inside the newm marketplace vault contract. These UTxOs are batcher specific and provide a method for NEWM to collect profit from successful purchase transactions. We suggest having at least 2 vault UTxOs for your batcher but as many as `delay_depth` + 1 UTxOs may be optimal.

The UTxOs are automatically tracked by the batcher. The only requirement is that the value of `batcher.hash` is inside the datum of these UTxOs.

Please refer to the [NEWM Marketplace Documentation](https://github.com/projectNEWM/newm-market/blob/master/README.md) about setting up these UTxOs.

## Running The Batcher

Running the batcher is as simple as entering the virtual environment and executing the `batcher.py` script.

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the batcher
python3 batcher.py
```

If the batcher can successfully start syncing blocks then it is working correctly.

Run the tests with `pytest`. Some tests require access to a full node.

## Running NEWM Batcher As A Service

It is suggested to run the NEWM batcher as a service on your server. Below are instructions to modifying the `newm-batcher.service` file.

1. Update newm-batcher.service file with correct absolute paths to the repo directory. The User and Group need to be updated your information.

    ```
    User              = your_username
    Group             = your_groupname
    Environment       = REPO_PATH=/absolute/path/to/your/application
    WorkingDirectory  = /absolute/path/to/your/application
    ```

2. Save the service file, copy it to the correct location, and enable the service\.

    ```sh
    sudo cp newm-batcher.service /etc/systemd/system/newm-batcher.service
    sudo chmod 644 /etc/systemd/system/newm-batcher.service
    sudo systemctl daemon-reload
    sudo systemctl enable newm-batcher.service
    sudo systemctl start newm-batcher.service
    ```

3. Verify the service status:

    ```sh
    sudo systemctl status newm-batcher.service
    ```

The service can be followed with the `follow_batcher.sh` script.

## Using DB Analysis Tool

The NEWM batcher comes with an db analysis tool to query the batcher db without stopping the batcher. This can be very useful for debugging, checking balances, batcher status, and getting the current marketplace state.

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the batcher
python3 analysis.py --help
```

```
usage: analysis.py [-h] [-s] [--batcher] [--oracle] [--data] [--sales] [--vault] [--references] [--query-sale TKN] [--query-order TAG] [--sorted-queue] [--simulate-purchase TKN TAG] [--simulate-refund TKN TAG]

NEWM-Batcher Database Analysis Tool

options:
  -h, --help                  show this help message and exit
  -s, --status                return the current sync status
  --batcher                   return the batcher UTxOs
  --oracle                    return the oracle UTxO
  --data                      return the data UTxO
  --sales                     return the sale UTxOs and queue entries
  --vault                     return the vault UTxOs
  --references                return the reference UTxOs
  --query-sale TKN            return the queue entries for a sale
  --query-order TAG           return the queue info for a queue entry
  --sorted-queue              return the sorted sale UTxOs and queue entries
  --simulate-purchase TKN TAG simulate the purchase endpoint
  --simulate-refund TKN TAG   simulate the purchase endpoint
```

## Updating The NEWM Batcher

There may be updates to the batcher from time to time. Below are instructions to update your current batcher to the newest version.

```bash
# Step 1: Checkout their personal branch
git checkout your-personal-branch

# Step 2: Pull the latest changes from the main branch
git pull origin master

# Step 3: Stash the config.yaml file to preserve it
git stash push -m "Save config.yaml" config.yaml

# Step 4: Merge the main branch into their personal branch
git merge master

# Step 5: Apply the stashed config.yaml file to restore it
git stash pop

# Step 6: Stage and commit the changes
git add .

git commit -m "Merged main branch while keeping config.yaml unchanged"
```

The goal of an update is to perserve the config.yaml file while updating everything else.

### Resetting The NEWM Batcher DB

If a complete db reset is required use the command below.

```bash
rm *.log
rm batcher.db
```

## Running NEWM Batcher With Docker

**Docker is not support as of right now**

<!-- Build, create, and run docker:
```bash
docker build -t newm-batcher .

docker volume create batcher-data

docker run -it --rm \
    -v /path/to/node/db-folder:/root/node \
    -v batcher-data:/root/newm-batcher \
    -v /path/to/newm-batcher-v1/config.yaml:/root/newm-batcher/config.yaml \
    --name newm-batcher-container \
    newm-batcher
```

Removing the volume:
```bash
docker volume rm batcher-data
```

Accessing it via:
```bash
docker exec -it newm-batcher-container /bin/bash
```

Use then analysis file while inside the container:
```bash
source venv/bin/activate
python3 analysis.py --help
``` -->


