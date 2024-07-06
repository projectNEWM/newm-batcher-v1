import pytest

from src.datums import get_incentive_amount, queue_validity, sale_validity


@pytest.fixture
def good_sale_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "39f29cfe6ab0765578a6e0d8871e1a3bc18f5d277b257095aabf1cd8"
                    },
                    {
                        "bytes": ""
                    }
                ]
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "85510e059114a9dcdf7c1d842a1b8fdfd2438cd31ef1b3edcf6d5d67"
                    },
                    {
                        "bytes": "001bc280002699546a3f2b852e6d2543659ede8722ea06251ef1e7fd94aeae27"
                    },
                    {
                        "int": 1
                    }
                ]
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
                        "int": 1
                    }
                ]
            },
            {
                "int": 100000000
            }
        ]
    }


@pytest.fixture
def bad_sale_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": ""
                    },
                    {
                        "bytes": ""
                    }
                ]
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
                        "int": 0
                    }
                ]
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
                        "int": 0
                    }
                ]
            },
            {
                "int": 0
            }
        ]
    }


@pytest.fixture
def good_queue_datum():
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
def bad_queue_datum():
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


def test_is_good_queue_datum_valid(good_queue_datum):
    result = queue_validity(good_queue_datum)
    assert result is True


def test_can_get_incentive(good_queue_datum):
    amt, priority = get_incentive_amount(good_queue_datum)
    assert amt == 1000000
    assert priority == 0


def test_is_bad_queue_datum_invalid(bad_queue_datum):
    result = queue_validity(bad_queue_datum)
    assert result is False


def test_is_good_sale_datum_valid(good_sale_datum):
    result = sale_validity(good_sale_datum)
    assert result is True


def test_is_bad_sale_datum_valid(bad_sale_datum):
    result = sale_validity(bad_sale_datum)
    assert result is False
