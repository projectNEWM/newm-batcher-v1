import os

import pytest

from src import cli
from tests.helpers import is_node_live


@pytest.fixture
def test_signed_file_path():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx.signed')


@pytest.fixture
def test_draft_file_path():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx.draft')


@pytest.fixture
def test_skey_file_path():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_payment.skey')


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


def test_query_mempool_with_no_socket(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_tx_mempool("", config["tx_id"], config["file_path"], config["network"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_is_tx_exists_in_mempool(live_node):
    result = cli.does_tx_exists_in_mempool(live_node["socket"], live_node["tx_id"], live_node["file_path"], live_node["network"])
    assert result is False


def test_query_tip_with_no_socket(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_tip("", config["file_path"], config["network"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_get_latest_block_number(live_node):
    result = cli.get_latest_block_number(live_node["socket"], live_node["file_path"], live_node["network"])
    assert result > 0


def test_tx_id_of_no_file():
    with pytest.raises(SystemExit) as excinfo:
        cli.txid("")
        assert excinfo.value.code == 1


def test_tx_id_of_test_file(test_signed_file_path):
    result = cli.txid(test_signed_file_path)
    answer = "1c471e439d9bfea40eb818e8dd2cb2ec081c3858ca5d92b51f2ec028ff0a1e89"
    assert result == answer
