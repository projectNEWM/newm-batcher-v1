import os

import pytest

from src.tx_simulate import (get_cbor_from_file, get_index_in_order,
                             inputs_from_cbor, resolve_inputs,
                             sort_lexicographically, to_bytes)


@pytest.fixture
def test_draft_file_path():
    return os.path.join(os.path.dirname(__file__), 'test_files', 'test_tx2.draft')


def test_resolve_inputs_from_test_tx_cbor():
    cborHex = "84a700828258204f2f4df5ab187b8438ebaa38859f739f4129609029856a38b11bdf8561b6ea6f018258204f2f4df5ab187b8438ebaa38859f739f4129609029856a38b11bdf8561b6ea6f020d818258201e0b413409dd9591b2a69bca80d7d776e8bb5130f02af0bf886e08ce5b6e183a0012838258204f2f4df5ab187b8438ebaa38859f739f4129609029856a38b11bdf8561b6ea6f0082582069617d2a5ede6fc9064007342ea3ca81000cf5756624f25ade9aaad3e0469fd2018258208044b953a8d0f92102ba47be9bb1479714cdc277dc03b190c1e8dbcce5b751a500018282581d60e154dbd9ee8685258d7be1d3f374e4c2f1aebeada68707113b1422b0821a00465f5ca2581c36bd690356f3dfd216c6cf0aba028f5626a0802e6f898f36c78bd682a15820affab1e0005e77ab1e007207812dd784991aa6bd0584b7ef4be68be92029fa8201581c769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcffa145744e45574d1a0112a88082581d600d28d4a2e4c1504b8bf77f7db89561ca6421eef8ee1ea5a99300e88e821a0037ac30a2581c769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcffa145744e45574d190c0b581cdfff8bc9cdfa7eb004eab6c303984b8e7b6f7cf3337f17826a23c1e2a15820001bc28000a5125631842958ab17da111bd82c01543c84083fed0be251a821a21a0001e1b9021a000557300e82581cc59da4ec6e515c2efc8866274dee6ac9a64b5945efd365f3a999e760581ce154dbd9ee8685258d7be1d3f374e4c2f1aebeada68707113b1422b00b5820af4a8428559ecd3197627d234501c2ea6d5d7ad6a348e8869be7a5bc1480bc0fa10581840000d87a80821a0016e3601a1dcd6500f5f6"
    inputs = resolve_inputs(cborHex)
    assert len(inputs) == 6


def test_resolve_inputs_from_test_tx_file(test_draft_file_path):
    cborHex = get_cbor_from_file(test_draft_file_path)
    inputs, inputs_cbor = inputs_from_cbor(cborHex)
    answer = "868258204f2f4df5ab187b8438ebaa38859f739f4129609029856a38b11bdf8561b6ea6f018258204f2f4df5ab187b8438ebaa38859f739f4129609029856a38b11bdf8561b6ea6f028258201e0b413409dd9591b2a69bca80d7d776e8bb5130f02af0bf886e08ce5b6e183a008258204f2f4df5ab187b8438ebaa38859f739f4129609029856a38b11bdf8561b6ea6f0082582069617d2a5ede6fc9064007342ea3ca81000cf5756624f25ade9aaad3e0469fd2018258208044b953a8d0f92102ba47be9bb1479714cdc277dc03b190c1e8dbcce5b751a500"
    assert len(inputs) == 6
    assert inputs_cbor == answer


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
