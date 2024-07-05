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


def test_create_batcher(db_manager, sample_value):
    tag = "acab"
    txid = "test_txid"
    db_manager.create_batcher(tag, txid, sample_value)
    pid = "acab"

    record = db_manager.read_batcher(pid)
    assert record['tag'] == tag
    assert record['txid'] == txid
    assert record['value'] == sample_value

    records = db_manager.read_all_batcher()
    assert len(records) == 1
    assert records[0] == record


def test_delete_batcher(db_manager, sample_value):
    tag = "acab"
    txid = "test_txid"
    db_manager.create_batcher(tag, txid, sample_value)
    pid = "acab"

    delete_flag = db_manager.delete_batcher(tag)
    record = db_manager.read_batcher(pid)
    assert record is None
    assert delete_flag is True


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

    records = db_manager.read_all_sale_tkns()
    assert len(records) == 1
    assert records[0] == tkn


def test_delete_sale(db_manager, sample_value):
    tkn = "test_tkn"
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.create_sale_record(tkn, txid, datum, sample_value)

    delete_flag = db_manager.delete_sale_by_txid(txid)
    record = db_manager.read_sale_record(tkn)
    assert record is None
    assert delete_flag is True


def test_create_queue():
    pass


def test_delete_queue():
    pass


def test_read_queue():
    pass


def test_read_all_queue():
    pass


def test_create_seend():
    pass


def test_read_seen():
    pass
