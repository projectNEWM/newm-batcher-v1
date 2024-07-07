import pytest
from pycardano import Network

from src.address import from_pkh_sc, pkh_from_address


def test_pkh_from_base_address():
    addr = "addr_test1qrvnxkaylr4upwxfxctpxpcumj0fl6fdujdc72j8sgpraa9l4gu9er4t0w7udjvt2pqngddn6q4h8h3uv38p8p9cq82qav4lmp"
    pkh = "d9335ba4f8ebc0b8c9361613071cdc9e9fe92de49b8f2a4782023ef4"
    result = pkh_from_address(addr)
    assert result == pkh


def test_pkh_from_enterprise_address():
    addr = "addr_test1vrs4fk7ea6rg2fvd00sa8um5unp0rt474kngwpc38v2z9vqujprdk"
    pkh = "e154dbd9ee8685258d7be1d3f374e4c2f1aebeada68707113b1422b0"
    result = pkh_from_address(addr)
    assert result == pkh


def test_from_pkh_sc_without_staking():
    pkh = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef01"
    sc = ""
    network = Network.TESTNET
    result = from_pkh_sc(pkh, sc, network)
    answer = "addr_test1vz4ummcpydzk0zdtehhszg69v7y6hn00qy352euf40x77qgmly3us"
    assert isinstance(result, str)
    assert result == answer


def test_from_pkh_sc_with_staking():
    pkh = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef01"
    sc = "123456789abcdef0123456789abcdef0123456789abcdef012345678"
    network = Network.TESTNET
    result = from_pkh_sc(pkh, sc, network)
    answer = "addr_test1qz4ummcpydzk0zdtehhszg69v7y6hn00qy352euf40x77qgjx3t83x4ummcpydzk0zdtehhszg69v7y6hn00qy352euqhrykfn"
    assert isinstance(result, str)
    assert result == answer


def test_from_pkh_sc_invalid_pkh():
    pkh = "invalid_pkh"
    sc = ""
    network = Network.TESTNET
    with pytest.raises(ValueError):
        from_pkh_sc(pkh, sc, network)


def test_from_pkh_sc_invalid_sc():
    pkh = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef01"
    sc = "invalid_sc"
    network = Network.TESTNET
    with pytest.raises(ValueError):
        from_pkh_sc(pkh, sc, network)
