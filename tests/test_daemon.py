import os

import pytest

from src.daemon import create_toml_file


@pytest.fixture
def cleanup():
    yield
    if os.path.exists('test_daemon.toml'):
        os.remove('test_daemon.toml')


def test_create_toml_file_defaults(cleanup):
    filename = 'test_daemon.toml'
    node_socket = '/tmp/node.socket'
    timestamp = 1625097600
    block_hash = 'abc123'

    create_toml_file(filename, node_socket, timestamp, block_hash)
    assert os.path.exists(filename)
