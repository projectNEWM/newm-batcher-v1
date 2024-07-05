import os

import pytest

from src.db_manager import DatabaseManager
from src.value import Value


@pytest.fixture
def cleanup():
    yield
    if os.path.exists('test_batcher.db'):
        os.remove('test_batcher.db')


@pytest.fixture
def config():
    return {
        "starting_block_number": 0,
        "starting_blockhash": "acab",
        "starting_timestamp": 1
    }


@pytest.fixture
def db_manager(cleanup):
    manager = DatabaseManager(db_file='test_batcher.db')
    yield manager
    manager.cleanup()


@pytest.fixture
def sample_value():
    return Value({"acab": {"acab": 1}})


def test_initialize_status_and_read(db_manager, config):
    db_manager.initialize_status(config)
    record = db_manager.read_status()
    assert record['block_number'] == config['starting_block_number']
    assert record['block_hash'] == config['starting_blockhash']
    assert record['timestamp'] == config['starting_timestamp']


def test_update_status_and_read(db_manager, config):
    db_manager.initialize_status(config)
    block_number = 2
    block_hash = "fade"
    timestamp = 4
    db_manager.update_status(block_number, block_hash, timestamp)
    record = db_manager.read_status()
    assert record['block_number'] == block_number
    assert record['block_hash'] == block_hash
    assert record['timestamp'] == timestamp


def test_create_batcher():
    pass


def test_delete_batcher():
    pass


def test_read_batcher():
    pass


def test_read_all_batcher():
    pass


def test_create_sale_record(db_manager, sample_value):
    tkn = "test_tkn"
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.create_sale_record(tkn, txid, datum, sample_value)

    record = db_manager.read_sale_record(tkn)
    assert record is not None
    assert record['txid'] == txid
    assert record['datum'] == datum
    assert record['value'] == sample_value
