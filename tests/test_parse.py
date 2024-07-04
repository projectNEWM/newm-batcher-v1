import pytest

from src.parse import asset_list_to_dict
from src.value import Value


@pytest.fixture
def generate_test_data():
    return [
        {
            "policy": "4d6d1192d39a48f4c80edbe52a5c480bec0a4e0711a998ca016b81a5",
            "asset": "001bc28001047a0269ba71359397cf9b3dd1124cbed1b1454cee335ab7ef91f8",
            "asset_ascii": None,
            "amount": 100000000
        },
        {
            "policy": "5d6d1192d39a48f4c80edbe52a5c480bec0a4e0711a998ca016b81a6",
            "asset": "101bc28001047a0269ba71359397cf9b3dd1124cbed1b1454cee335ab7ef91f9",
            "asset_ascii": None,
            "amount": 50000000
        }
    ]


def test_asset_list_to_dict(generate_test_data):
    assets = generate_test_data

    expected_result = {
        "4d6d1192d39a48f4c80edbe52a5c480bec0a4e0711a998ca016b81a5": {
            "001bc28001047a0269ba71359397cf9b3dd1124cbed1b1454cee335ab7ef91f8": 100000000
        },
        "5d6d1192d39a48f4c80edbe52a5c480bec0a4e0711a998ca016b81a6": {
            "101bc28001047a0269ba71359397cf9b3dd1124cbed1b1454cee335ab7ef91f9": 50000000
        }
    }

    result = asset_list_to_dict(assets)
    assert result == Value(expected_result)


def test_empty_asset_list_to_dict():

    expected_result = {}

    result = asset_list_to_dict([])
    assert result == Value(expected_result)
