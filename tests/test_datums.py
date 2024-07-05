import pytest

from src.datums import get_incentive_amount, queue_validity


@pytest.fixture
def good_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "0d28d4a2e4c1504b8bf77f7db89561ca6421eef8ee1ea5a99300e88e"
                    },
                    {
                        "bytes": ""
                    }
                ]
            },
            {
                "int": 1234567
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff"
                    },
                    {
                        "bytes": "744e45574d"
                    },
                    {
                        "int": 1000000
                    }
                ]
            },
            {
                "bytes": "ca11ab1e0081db953e0a5384d76d24eb7fbafbea8a109bbc61d82596fafcfb60"
            }
        ]
    }


@pytest.fixture
def bad_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "0d28d4a2e4c1504b8bf77f7db89561ca6421eef8ee1ea5a99300e88e"
                    },
                    {
                        "bytes": ""
                    }
                ]
            },
            {
                "int": 1234567
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": ""
                    },
                    {
                        "bytes": ""
                    },
                    {
                        "int": 1
                    }
                ]
            },
            {
                "bytes": ""
            }
        ]
    }


def test_is_good_queue_datum_valid(good_datum):
    result = queue_validity(good_datum)
    assert result is True


def test_can_get_incentive(good_datum):
    result = get_incentive_amount(good_datum)
    assert result == 1000000


def test_is_bad_queue_datum_invalid(bad_datum):
    result = queue_validity(bad_datum)
    assert result is False
