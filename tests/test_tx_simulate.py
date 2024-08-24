import os

import pytest

from src.tx_simulate import (get_cbor_from_file, get_index_in_order,
                             inputs_from_cbor, resolve_inputs,
                             sort_lexicographically, to_bytes)


@pytest.fixture
def test_draft_file_path1():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx3.draft')


@pytest.fixture
def test_draft_file_path2():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx2.draft')


def test_resolve_inputs_from_test_tx_cbor1(test_draft_file_path1):
    cborHex = get_cbor_from_file(test_draft_file_path1)
    inputs = resolve_inputs(cborHex)
    assert len(inputs) == 10


def test_resolve_inputs_from_test_tx_cbor2(test_draft_file_path2):
    cborHex = get_cbor_from_file(test_draft_file_path2)
    inputs = resolve_inputs(cborHex)
    assert len(inputs) == 6


def test_resolve_inputs_from_test_tx_file1(test_draft_file_path1):
    cborHex = get_cbor_from_file(test_draft_file_path1)
    inputs, inputs_cbor = inputs_from_cbor(cborHex)
    assert len(inputs) == 10


def test_resolve_inputs_from_test_tx_file2(test_draft_file_path2):
    cborHex = get_cbor_from_file(test_draft_file_path2)
    inputs, inputs_cbor = inputs_from_cbor(cborHex)
    assert len(inputs) == 6


def test_empty_string_bytes():
    string = ""
    assert to_bytes(string) == b''
    assert to_bytes(string).hex() == string


def test_simple_string_bytes():
    string = "acab"
    assert to_bytes(string) == b'\xac\xab'
    assert to_bytes(string).hex() == string


def test_bad_string_bytes():
    string = "cab"
    # Assert that a ValueError is raised
    with pytest.raises(ValueError, match="non-hexadecimal number found in fromhex()"):
        to_bytes(string)


def test_single_item_is_first():
    x = "9ac0928f338ec0c4f5ae1275fe6517881a9c842c07720097ffc4f5fb82975dc1#0"

    # Get the ordered list of strings
    ordered_list = sort_lexicographically(x)

    # Get and print the index of each string
    index_x = get_index_in_order(ordered_list, x)
    assert index_x == 0


def test_three_unique_items():
    x = "d4c1747f2a6dea8f307f4846dab721798f141aeb156cb24221c5671548e6cf7e#0"
    y = "a1133d386f47a72edd05d964540fe9763552685ca9ffbf07b26770766d063009#0"
    z = "9ac0928f338ec0c4f5ae1275fe6517881a9c842c07720097ffc4f5fb82975dc1#0"

    # Get the ordered list of strings
    ordered_list = sort_lexicographically(x, y, z)

    # Get and print the index of each string
    index_x = get_index_in_order(ordered_list, x)
    index_y = get_index_in_order(ordered_list, y)
    index_z = get_index_in_order(ordered_list, z)
    assert index_x == 2
    assert index_y == 1
    assert index_z == 0


def test_same_id_different_idx():
    x = "d4c1747f2a6dea8f307f4846dab721798f141aeb156cb24221c5671548e6cf7e#0"
    y = "d4c1747f2a6dea8f307f4846dab721798f141aeb156cb24221c5671548e6cf7e#1"
    z = "d4c1747f2a6dea8f307f4846dab721798f141aeb156cb24221c5671548e6cf7e#2"

    # Get the ordered list of strings
    ordered_list = sort_lexicographically(x, y, z)

    # Get and print the index of each string
    index_x = get_index_in_order(ordered_list, x)
    index_y = get_index_in_order(ordered_list, y)
    index_z = get_index_in_order(ordered_list, z)
    assert index_x == 0
    assert index_y == 1
    assert index_z == 2
