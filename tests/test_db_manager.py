import os

import pytest

from src.db_manager import DbManager
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
def db_manager(cleanup, config):
    manager = DbManager(db_file='test_batcher.db')
    manager.initialize(config)
    yield manager
    manager.cleanup()


@pytest.fixture
def sample_value():
    return Value({"acab": {"acab": 1}})


def test_initialize_status_and_read(db_manager, config):
    db_manager.status.load(config)
    record = db_manager.status.read()
    assert record['block_number'] == config['starting_block_number']
    assert record['block_hash'] == config['starting_blockhash']
    assert record['timestamp'] == config['starting_timestamp']


def test_update_status_and_read(db_manager, config):
    db_manager.status.load(config)
    block_number = 2
    block_hash = "fade"
    timestamp = 4
    db_manager.status.update(block_number, block_hash, timestamp)
    record = db_manager.status.read()
    assert record['block_number'] == block_number
    assert record['block_hash'] == block_hash
    assert record['timestamp'] == timestamp


def test_create_batcher(db_manager, sample_value):
    tag = "acab"
    txid = "test_txid"
    db_manager.batcher.create(tag, txid, sample_value)
    pid = "acab"

    record = db_manager.batcher.read(pid)
    assert record['tag'] == tag
    assert record['txid'] == txid
    assert record['value'] == sample_value

    records = db_manager.batcher.read_all()
    assert len(records) == 1
    assert records[0] == record


def test_delete_batcher(db_manager, sample_value):
    tag = "acab"
    txid = "test_txid"
    db_manager.batcher.create(tag, txid, sample_value)
    pid = "acab"

    delete_flag = db_manager.batcher.delete(tag)
    record = db_manager.batcher.read(pid)
    assert record is None
    assert delete_flag is True


def test_delete_batcher_non_existent(db_manager, sample_value):
    tag = "acab"
    txid = "test_txid"
    db_manager.batcher.create(tag, txid, sample_value)

    delete_flag = db_manager.batcher.delete("")
    record = db_manager.batcher.read("")
    assert record is None
    assert delete_flag is False


def test_create_sale_record(db_manager, sample_value):
    tkn = "test_tkn"
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.sale.create(tkn, txid, datum, sample_value)

    record = db_manager.sale.read(tkn)
    assert record is not None
    assert record['txid'] == txid
    assert record['datum'] == datum
    assert record['value'] == sample_value

    records = db_manager.sale.read_all()
    assert len(records) == 1
    assert records[0] == tkn


def test_delete_sale(db_manager, sample_value):
    tkn = "test_tkn"
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.sale.create(tkn, txid, datum, sample_value)

    delete_flag = db_manager.sale.delete(txid)
    record = db_manager.sale.read(tkn)
    assert record is None
    assert delete_flag is True


def test_create_queue(db_manager, sample_value):
    tag = "acab"
    tkn = "test_tkn"
    txid = "test_txid"
    datum = {"key": "value"}
    timestamp = 1
    tx_idx = 0
    db_manager.queue.create(tag, txid, tkn, datum, sample_value, timestamp, tx_idx)

    record = db_manager.queue.read(tag)
    assert record is not None
    assert record['txid'] == txid
    assert record['datum'] == datum
    assert record['value'] == sample_value

    records = db_manager.queue.read_all(tkn)
    assert len(records) == 1
    assert records[0][0] == tag


def test_delete_queue(db_manager, sample_value):
    tag = "acab"
    tkn = "test_tkn"
    txid = "test_txid"
    datum = {"key": "value"}
    timestamp = 1
    tx_idx = 0
    db_manager.queue.create(tag, txid, tkn, datum, sample_value, timestamp, tx_idx)

    delete_flag = db_manager.queue.delete(tag)
    record = db_manager.queue.read(tag)
    assert record is None
    assert delete_flag is True


def test_create_seen(db_manager):
    tag = "acab"
    db_manager.seen.create(tag)

    record = db_manager.seen.read(tag)
    assert record is True


def test_create_oracle(db_manager):
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.oracle.create(txid, datum)

    record = db_manager.oracle.read()
    _txid = record['txid']
    _datum = record['datum']
    assert "" == _txid
    assert {} == _datum


def test_update_oracle(db_manager):
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.oracle.create(txid, datum)

    txid2 = "test_txid2"
    datum2 = {"key": "value2"}
    db_manager.oracle.update(txid2, datum2)

    record = db_manager.oracle.read()
    _txid = record['txid']
    _datum = record['datum']
    assert txid2 == _txid
    assert datum2 == _datum


def test_create_vault(db_manager, sample_value):
    tag = "acab"
    pkh = "acab"
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.vault.create(tag, txid, pkh, datum, sample_value)

    record = db_manager.vault.read(pkh)
    _txid = record['txid']
    _datum = record['datum']
    assert txid == _txid
    assert datum == _datum


def test_delete_vault(db_manager, sample_value):
    tag = "acab"
    pkh = "acab"
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.vault.create(tag, txid, pkh, datum, sample_value)

    delete_flag = db_manager.vault.delete(tag)
    record = db_manager.vault.read(pkh)
    assert record is None
    assert delete_flag is True


def test_create_data(db_manager):
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.data.create(txid, datum)

    record = db_manager.data.read()
    _txid = record['txid']
    _datum = record['datum']
    assert "" == _txid
    assert {} == _datum


def test_update_data(db_manager):
    txid = "test_txid"
    datum = {"key": "value"}
    db_manager.data.create(txid, datum)

    txid2 = "test_txid2"
    datum2 = {"key": "value2"}
    db_manager.data.update(txid2, datum2)

    record = db_manager.data.read()
    _txid = record['txid']
    _datum = record['datum']
    assert txid2 == _txid
    assert datum2 == _datum
