import os

import pytest

from src import cli
from tests.helpers import is_node_live


@pytest.fixture
def cleanup():
    yield
    if os.path.exists('output.file'):
        os.remove('output.file')


@pytest.fixture
def config(cleanup):
    return {
        "socket": "/home/logic/Documents/Work/LogicalMechanism/testnets/node-preprod/db-testnet/node.socket",
        "tx_id": "7b936e02a2cc738166f055b11b12623d51589152354c9233067d674c6c2beebd",
        "file_path": "output.file",
        "network": "--testnet-magic 1",
    }


@pytest.fixture
def live_node(config):
    if not is_node_live(config["socket"]):
        pytest.skip("Node is not live")
    return config


# run with or without node access
def test_check_mempool_with_no_socket(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_tx_mempool("", config["tx_id"], config["file_path"], config["network"])
        assert excinfo.value.code == 1


# run only with node access
@pytest.mark.live_node
def test_check_mempool_with_socket(live_node):
    result = cli.does_tx_exists_in_mempool(live_node["socket"], live_node["tx_id"], live_node["file_path"], live_node["network"])
    assert result is False
