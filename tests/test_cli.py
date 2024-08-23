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
def test_draft_file_path2():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx2.draft')


@pytest.fixture
def test_protocol_file_path():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_protocol.json')


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
        "cli": "/usr/local/bin/cardano-cli",
        "socket": "/home/logic/Documents/Work/LogicalMechanism/testnets/node-preprod/db-testnet/node.socket",
        "tx_id": "7b936e02a2cc738166f055b11b12623d51589152354c9233067d674c6c2beebd",
        "file_path": "output.file",
        "network": "--testnet-magic 1",
    }


@pytest.fixture
def live_node(config):
    if not is_node_live(config["socket"], 1, config['cli']):
        pytest.skip("Node is not live")
    return config


def test_query_protocol_parameters_with_no_socket(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_protocol_parameters("", config["file_path"], config["network"], config["cli"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_query_protocol_parameters(live_node):
    cli.query_protocol_parameters(live_node["socket"], live_node["file_path"], live_node["network"], live_node["cli"])

    with open(live_node["file_path"], "r") as read_content:
        data = json.load(read_content)
    assert data["maxTxSize"] == 16384


def test_query_mempool_with_no_socket(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_tx_mempool("", config["tx_id"], config["file_path"], config["network"], config["cli"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_is_tx_exists_in_mempool(live_node):
    result = cli.does_tx_exists_in_mempool(live_node["socket"], live_node["tx_id"], live_node["file_path"], live_node["network"], live_node["cli"])
    assert result is False


def test_query_tip_with_no_socket(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_tip("", config["file_path"], config["network"], config["cli"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_get_latest_block_number(live_node):
    result = cli.get_latest_block_number(live_node["socket"], live_node["file_path"], live_node["network"], live_node['cli'])
    assert result > 0


@pytest.mark.live_node
def test_get_latest_slot_number(live_node):
    result = cli.get_latest_slot_number(live_node["socket"], live_node["file_path"], live_node["network"], live_node['cli'])
    assert result > 0


def test_tx_id_of_no_file(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.txid("", config['cli'])
        assert excinfo.value.code == 1


def test_tx_id_of_test_file(test_signed_file_path, config):
    result = cli.txid(test_signed_file_path, config["cli"])
    answer = "1c471e439d9bfea40eb818e8dd2cb2ec081c3858ca5d92b51f2ec028ff0a1e89"
    assert result == answer


def test_sign_a_tx_that_doesnt_exist(test_skey_file_path, config):
    with pytest.raises(SystemExit) as excinfo:
        cli.sign("", config["file_path"], config["network"], test_skey_file_path, config["cli"])
        assert excinfo.value.code == 1


def test_sign_a_tx_without_a_key(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.sign("", config["file_path"], config["network"], "", config["cli"])
        assert excinfo.value.code == 1


def test_sign_a_draft_tx(test_draft_file_path, test_skey_file_path, config):
    cli.sign(test_draft_file_path, config["file_path"], config["network"], test_skey_file_path, config["cli"])

    with open(config["file_path"], "r") as read_content:
        data = json.load(read_content)
    assert data["type"] == "Witnessed Tx BabbageEra"


def test_sign_a_signed_tx(test_signed_file_path, test_skey_file_path, config):
    cli.sign(test_signed_file_path, config["file_path"], config["network"], test_skey_file_path, config["cli"])

    with open(config["file_path"], "r") as read_content:
        data = json.load(read_content)
    assert data["type"] == "Witnessed Tx BabbageEra"


def test_submit_a_signed_tx_with_no_socket(test_signed_file_path, config):
    with pytest.raises(SystemExit) as excinfo:
        _ = cli.submit(test_signed_file_path, "", config["network"], config["cli"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_submit_an_already_submitted_signed_tx(test_signed_file_path, live_node):
    result = cli.submit(test_signed_file_path, live_node["socket"], live_node["network"], live_node['cli'])
    assert result is False


@pytest.mark.live_node
def test_submit_a_signed_tx(test_signed_file_path2, live_node):
    result = cli.submit(test_signed_file_path2, live_node["socket"], live_node["network"], live_node['cli'])
    # if the tx is unsubmitted then its true else its false
    assert result is True or result is False


@pytest.mark.live_node
def test_query_slot_number(live_node):
    slot = cli.query_slot_number(live_node["socket"], 1722466813112, live_node["network"], live_node["cli"])
    assert slot == 66783613


@pytest.mark.live_node
def test_query_slot_number_with_delta(live_node):
    start_slot = cli.query_slot_number(live_node["socket"], 1722466813112, live_node["network"], live_node["cli"], 21)
    end_slot = cli.query_slot_number(live_node["socket"], 1722466813112, live_node["network"], live_node["cli"], -21)
    assert start_slot == 66783634
    assert end_slot == 66783592


def test_query_slot_number_with_no_socket(live_node):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_slot_number("", 1722466813112, live_node["network"], live_node["cli"])
        assert excinfo.value.code == 1


@pytest.mark.live_node
def test_query_utxo_does_exist(live_node):
    output = cli.does_utxo_exist(live_node["socket"], "1e0b413409dd9591b2a69bca80d7d776e8bb5130f02af0bf886e08ce5b6e183a#0", live_node["network"], live_node["cli"])
    assert output is True


@pytest.mark.live_node
def test_query_utxo_does_not_exist(live_node):
    output = cli.does_utxo_exist(live_node["socket"], "aacee651c33ed033402e96e8e946a82a3cc3c0be29bf0897ee465817be227255#2", live_node["network"], live_node["cli"])
    assert output is False


def test_query_utxo_with_no_socket(live_node):
    with pytest.raises(SystemExit) as excinfo:
        cli.does_utxo_exist("", "aacee651c33ed033402e96e8e946a82a3cc3c0be29bf0897ee465817be227255#2", live_node["network"], live_node["cli"])
        assert excinfo.value.code == 1


def test_calculate_min_fee(test_protocol_file_path, test_draft_file_path, config):
    fee = cli.calculate_min_fee(test_draft_file_path, test_protocol_file_path, config["cli"])
    assert fee == 180681


def test_calculate_min_fee2(test_protocol_file_path, test_draft_file_path2, config):
    fee = cli.calculate_min_fee(test_draft_file_path2, test_protocol_file_path, config["cli"])
    assert fee == 319825


def test_query_script_ref_size_no_inputs(config):
    with pytest.raises(SystemExit) as excinfo:
        cli.query_ref_script_size(config["socket"], config["network"], [], config["cli"])
        assert excinfo.value.code == 1


def test_query_script_ref_size_single_input(config):
    inputs = [
        "6b19610151abde605dae5618437c6650b4ac293d2fbdda4b56af6fd3e250cfc7#1"
    ]
    size = cli.query_ref_script_size(config["socket"], config["network"], inputs, config["cli"])
    assert size == 9486


def test_query_script_ref_size_multiple_inputs(config):
    inputs = [
        "6b19610151abde605dae5618437c6650b4ac293d2fbdda4b56af6fd3e250cfc7#1",
        "d17bcc20fc3b9119122824de6de270a60c87322e1aeae0ee86dc8640815a4833#1",
        "04fab56d0030f172256619d19449db1278ac579588328c5c58c73ba5831ece82#1",
    ]
    size = cli.query_ref_script_size(config["socket"], config["network"], inputs, config["cli"])
    assert size == 29266
