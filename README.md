# NEWM Market Batcher v1

This is the first version of the NEWM Market Batcher.

## Setup

```bash
# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt
```

Run the batcher with `python3 batcher.py`. Run the tests with `pytest`. Some tests require access to a full node.

## External Requirements

The batcher requires a fully-synced cardano node, cardano-cli, cardano-address, [Oura](https://github.com/txpipe/oura), [Aiken](https://github.com/aiken-lang/aiken), python3, yq, and jq. Cardano-address is provided with the batcher inside the keys folder. The cardano-cli and cardano-node are assumed to be on path.

### Required CLI Keys

The batcher comes with a setup helper file, `setup_keys.sh`, that will allow the batcher to use a CIP03 wallet to generate the required cardano-cli keys. The script will prompt the user with the message below.

```
Press 1 to generate a wallet, 2 to load a wallet, or any other key to exit.
```

If the user wishes to generate a wallet then press 1. It will display a seed phrase for the user to write down then it will generate the required keys. If the user wishes to use an existing wallet then press 2. It will prompt the user to type in there seed phrase in a single line with single spaces between each word. If entered correctly then the script will generate the required keys. Any other key will exit the script. The script is designed to prevent overwriting.

After successfully setting up the wallet, the keys folder will contain two sets of files, one for the batcher and the other for the collateral, corresponding to the zeroth and first key paths from the seed phrase.

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

The batcher address will hold a UTxO with the batcher certificate token and 5 ADA and the collateral address will hold a UTxO with 5 ADA. The balances of these addresses can be view with the `balances.sh` script located in the keys folder as well as the `analysis.py` file in the parent directory using the `python3 analysis.py --batcher` command.

Using the setup script is not required as any valid cli keys can be used for the batcher. It is provided as a way to help secure the keys incase of failure or emergency.

## Configuration

The `config.yaml` file is split into two parts. The user is expected to update just the top part that states `# Update Values For Your Batcher`. Configuring the batcher is placing the correct information into the fields below. The other information inside the `config.yaml` file does not need to be changed nor updated.

```yaml
# Batcher Information
batcher_address: ""
profit_address: ""

# Collat Wallet Information
collat_address: ""
collat_utxo: ""

# Node And Network Information
network: ""
socket_path: ""
cli_path: ""
```

If the `setup_keys.sh` script is used then follow the steps below.

Replace the `batcher_address` with value from the batcher.addr file and `collat_address` with value from the collat.addr. The profit address can be another base address from the CIP03 wallet or any address of your choosing. The `collat_utxo` has the form `id#idx` and it holds 5 ADA. It will be used in every smart contract transaction as the collateral. The `network` variable is a string of either `--mainnet` or `--testnet-magic 1`. The batcher is designed to run on mainnet and pre-production only. The `socket_path` is the absolute path to the node socket of the fully synced cardano node.

The batcher is ready to run after this information has been updated. Do not update any other variables as it may inhibit the batcher's ability to function.

## Running NEWM Batcher As A Service


1. Clone the repository and navigate to the project directory:

    ```sh
    git clone https://github.com/newm-batcher-v1.git
    cd newm-batcher-v1
    ```

2. Update newm-batcher.service file with correct absolute paths to the repo directory.

    ```
    Environment       = REPO_PATH=/absolute/path/to/your/application
    WorkingDirectory  = /absolute/path/to/your/application
    ```

3. Create the service file and enable the service:

    ```sh
    sudo cp newm-batcher.service /etc/systemd/system/newm-batcher.service
    sudo chmod 644 /etc/systemd/system/newm-batcher.service
    sudo systemctl daemon-reload
    sudo systemctl enable newm-batcher.service
    sudo systemctl start newm-batcher.service
    ```

4. Verify the service status:

    ```sh
    sudo systemctl status newm-batcher.service
    ```

## Running NEWM Batcher With Docker

Build, create, and run docker:
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
```


## Updating The NEWM Batcher

There may be updates to the batcher from time to time. Below are instructions to update your current batcher to the newest version.

- TODO