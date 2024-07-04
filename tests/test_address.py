import pytest
from pycardano import Network

from src.address import from_pkh_sc


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
