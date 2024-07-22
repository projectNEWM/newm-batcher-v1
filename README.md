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

The batcher will require full node socket access, cardano-cli, [Oura](https://github.com/txpipe/oura), python3, yq, and jq.

### Required CLI Keys

- TODO

### Required API Keys

- TODO

## Configuration

- TODO

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
