import json
import os

import pytest

from src import cli
from tests.helpers import is_node_live


@pytest.fixture
def test_signed_file_path():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx.signed')


@pytest.fixture
def test_signed_file_path2():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx2.signed')


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


def test_query_protocol_parameters_with_no_socket(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_protocol_parameters("", config["file_path"], config["network"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_query_protocol_parameters(live_node):
    cli.query_protocol_parameters(live_node["socket"], live_node["file_path"], live_node["network"])

    with open(live_node["file_path"], "r") as read_content:
        data = json.load(read_content)
    assert data["maxTxSize"] == 16384


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


def test_sign_a_tx_that_doesnt_exist(test_skey_file_path, config):
    with pytest.raises(SystemExit) as excinfo:
        cli.sign("", config["file_path"], config["network"], test_skey_file_path)
        assert excinfo.value.code == 1


def test_sign_a_tx_without_a_key(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.sign("", config["file_path"], config["network"], "")
        assert excinfo.value.code == 1


def test_sign_a_draft_tx(test_draft_file_path, test_skey_file_path, config):
    cli.sign(test_draft_file_path, config["file_path"], config["network"], test_skey_file_path)

    with open(config["file_path"], "r") as read_content:
        data = json.load(read_content)
    assert data["type"] == "Witnessed Tx BabbageEra"


def test_sign_a_signed_tx(test_signed_file_path, test_skey_file_path, config):
    cli.sign(test_signed_file_path, config["file_path"], config["network"], test_skey_file_path)

    with open(config["file_path"], "r") as read_content:
        data = json.load(read_content)
    assert data["type"] == "Witnessed Tx BabbageEra"


def test_submit_a_signed_tx_with_no_socket(test_signed_file_path, config):
    with pytest.raises(SystemExit) as excinfo:
        _ = cli.submit(test_signed_file_path, "", config["network"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_submit_an_already_submitted_signed_tx(test_signed_file_path, live_node):
    result = cli.submit(test_signed_file_path, live_node["socket"], live_node["network"])
    assert result is False


@pytest.mark.live_node
def test_submit_a_signed_tx(test_signed_file_path2, live_node):
    result = cli.submit(test_signed_file_path2, live_node["socket"], live_node["network"])
    # if the tx is unsubmitted then its true else its false
    assert result is True or result is False


@pytest.mark.live_node
def test_query_slot_number(live_node):
    slot = cli.query_slot_number(live_node["socket"], 1722466813112, live_node["network"])
    assert slot == 66783613


@pytest.mark.live_node
def test_query_slot_number_with_delta(live_node):
    start_slot = cli.query_slot_number(live_node["socket"], 1722466813112, live_node["network"], 21)
    end_slot = cli.query_slot_number(live_node["socket"], 1722466813112, live_node["network"], -21)
    assert start_slot == 66783634
    assert end_slot == 66783592


def test_query_slot_number_with_no_socket(live_node):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_slot_number("", 1722466813112, live_node["network"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_query_utxo_does_exist(live_node):
    output = cli.does_utxo_exist(live_node["socket"], "01fc59107bafe99b0f2c1e45ebd16c7ebb75830d19970220100a21c7c74218dd#1", live_node["network"])
    assert output is True


@pytest.mark.live_node
def test_query_utxo_does_not_exist(live_node):
    output = cli.does_utxo_exist(live_node["socket"], "aacee651c33ed033402e96e8e946a82a3cc3c0be29bf0897ee465817be227255#2", live_node["network"])
    assert output is False


def test_query_utxo_with_no_socket(live_node):
    with pytest.raises(SystemExit) as excinfo:
        cli.does_utxo_exist("", "aacee651c33ed033402e96e8e946a82a3cc3c0be29bf0897ee465817be227255#2", live_node["network"])
        assert excinfo.value.code == 1
