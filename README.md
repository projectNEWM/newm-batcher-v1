# NEWM Market Batcher v1

NEWM-Batcher-V1 is the first version of the [NEWM Marketplace](https://github.com/projectNEWM/newm-market) order batcher. This lightweight tool processes orders using the sale and query contracts, prioritizing queue entries with larger incentives. It features automatic profit accumulation, a multi-asset incentive list, and arbitrary transaction simulation. Fulfilling orders with the batcher requires a batcher certificate, obtained by locking a complete NEWM Monster set into the band-lock-up contract in the marketplace. The batcher is designed to run alongside a fully synced node.

## Batcher Setup

Clone the repo and create your branch for the batcher.

```bash
git clone https://github.com/newm-batcher-v1.git
cd newm-batcher-v1
git checkout -b your-personal-branch
```

The batcher requires a fully synced cardano node and requires cardano-cli, cardano-address, [Ogmios](https://github.com/CardanoSolutions/ogmios), [Oura](https://github.com/txpipe/oura), [Aiken](https://github.com/aiken-lang/aiken), python3, yq, jq, and sponge.

The batcher has a setup helper file, `setup.sh`. This file will check and download all required external binaries. It will create the Python virtual environment and install the required modules. The setup script requires that the cardano node is already running and is fully synced. This file will auto-setup the entire batcher step-by-step.

The `config.yaml` file is split into two parts. The user is expected to run the `setup.sh` script to update the top part, which states `# Update Values For Your Batcher`. Configuring the batcher means entering the correct information into the fields below. The other information inside the `config.yaml` file does not need to be changed or updated.

**The current version of the batcher is designed to run on pre-production or mainnet only.**

### Binary Paths

The `config.yaml` file needs to have have absolute paths for all the binaries and required files.

```yaml
# Bin Paths; Need To be Absolute
cli_path: "/bin/cardano-cli"
oura_path: "/bin/oura"
ogmios_path: "/bin/ogmios"
aiken_path: "/bin/aiken"
addr_path: "/bin/cardano-address"

# File Paths; Needs To Be Absolute
socket_path: "/node.socket"
node_config_path: "/config.json"
```

### Required CLI Keys

The setup helper file, `setup.sh`, has a wallet generator inside of it, allowing the batcher to use a CIP03 wallet to generate the required cardano-cli keys. The script will prompt the user with the message below.

```bash
Press 1 to generate a wallet, 2 to load a wallet, or any other key to exit.
```

If the user wishes to generate a wallet, press 1. It will display a seed phrase for the user to write down, and then it will generate the required keys. If the user wishes to use an existing wallet, press 2. It will prompt the user to type in their seed phrase in a single line with single spaces between each word. If entered correctly, the script will generate the required keys.

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

The batcher address in `batcher.addr` will hold a single UTxO with the batcher certificate token and at least 5 ADA. The collateral address in `collat.addr` will have a single UTxO with at least 5 ADA. The balances of these addresses can be viewed with the `balances.sh` script located in the `keys` folder and the `analysis.py` file in the parent directory using the `python3 analysis.py --batcher` command. If using the `setup.sh` script then the UTxOs will be auto-generated.

The setup script is not required, as any valid cli keys can be used for the batcher. It is provided to help secure the keys in case of failure or emergency. The only requirement is that the skeys have the `batcher` and `collat` naming scheme.

### Obtaining A Batcher Certificate

A batcher certificate is issued when a user obtains a complete set of NEWM monsters and locks the entire band into a contract. The locking transaction mints a complete assets token that lives on the band lock UTxO and mints one batcher certificate to the user. The batcher certificate is tradable, allowing anyone who holds it to earn the ability to run a batcher. It can be burned at any time to unlock the NEWM monsters that created it, but it can only unlock the band with the matching completed assets token. This preserves ownership even after trading.

A batcher cannot batch without the token.

Please refer to the [NEWM Marketplace Documentation](https://github.com/projectNEWM/newm-market/blob/master/README.md#newm-monster-band-lock-up) about locking up the band.

### Setting Up The Vaults

The `setup.sh` script creates the vault UTxOs inside the newm vault contract. These UTxOs are batcher-specific and provide a method for NEWM to collect profit from successful purchase transactions. We suggest having at least two vault UTxOs for your batcher, but as many as `delay_depth` + 1 UTxOs may be optimal.

The batcher automatically tracks the UTxOs. The only requirement is that the value of `batcher.hash` is inside the datum of these UTxOs.

Please use the [NEWM Marketplace Documentation](https://github.com/projectNEWM/newm-market/blob/master/README.md#setting-up-vault-utxos) to set up these UTxOs.

## Running The Batcher

Running the batcher is as simple as entering the virtual environment and executing the `batcher.py` script.

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the batcher
python3 batcher.py
```

If the batcher can successfully start syncing blocks, it works correctly.

Tests can be run with `pytest`. Some tests require access to a full node.

If `ModuleNotFoundError: No module named 'pkg_resources'` appears then the setuptools needs to be upgraded.

```bash
# Activate the virtual environment
source venv/bin/activate

# Update setup tools
pip install --upgrade setuptools
```

## Running NEWM Batcher As A Service

It would be best to run the NEWM batcher as a service on your server. Below are instructions for modifying the `newm-batcher.service` file.

1. Update the newm-batcher.service file with correct absolute paths to the repo directory and your information for the User and Group.

    ```
    User              = your_username
    Group             = your_groupname
    Environment       = REPO_PATH=/absolute/path/to/your/application
    WorkingDirectory  = /absolute/path/to/your/application
    ```

2. Save the service file, copy it to the correct location, and enable the service.

    ```sh
    sudo cp -p newm-batcher.service /etc/systemd/system/newm-batcher.service
    sudo chmod 644 /etc/systemd/system/newm-batcher.service
    sudo systemctl daemon-reload
    sudo systemctl enable newm-batcher.service
    sudo systemctl start newm-batcher.service
    ```

3. Verify the service status:

    ```sh
    sudo systemctl status newm-batcher.service
    ```

4. The batcher can be stopped with

    ```sh
    sudo systemctl stop newm-batcher.service
    ```

The service can be monitored with the `follow_batcher.sh` script.

## Using DB Analysis Tool

The NEWM batcher comes with a database analysis tool that queries the batcher database without stopping the batcher. This can be very useful for debugging, checking balances, checking batcher status, and getting the current marketplace state.

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

Example:

```bash
python3 analysis.py --status
Batcher Is Synced
Current Status: {'block_number': 2650413, 'block_hash': '3a7b8768925480a9b1dd8ec6145bba9129011e001a1b6e94e133daf328ca6d3d', 'timestamp': 69611826}
```

## Updating The NEWM Batcher

The batcher may be updated from time to time. Below are instructions on updating your current batcher to the newest version.

```bash
# Step 1: Checkout your branch
git checkout your-personal-branch

# Step 2: Pull the latest changes from the main branch
git pull origin master

# Step 3: Stash the config.yaml file to preserve it
git stash push -m "Save config.yaml" config.yaml

# Step 4: Merge the main branch into their branch
git merge master

# Step 5: Apply the stashed config.yaml file to restore it
git stash pop

# Step 6: Stage and commit the changes
git add .

git commit -m "Merged main branch while keeping config.yaml unchanged"
```

The goal of an update is to preserve the config.yaml file while updating everything else.

### Resetting The NEWM Batcher DB

If a complete db reset is required, use the command below. Be sure to stop the batcher with Ctrl-C or with `sudo systemctl stop newm-batcher.service` before resetting the database.

```bash
rm *.log
rm batcher.db
```
