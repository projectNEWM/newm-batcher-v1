import pytest

from src.datums import (data_validity, get_incentive_amount, oracle_validity,
                        queue_validity, sale_validity, vault_validity)


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


@pytest.fixture
def good_vault_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "bytes": "e154dbd9ee8685258d7be1d3f374e4c2f1aebeada68707113b1422b0"
            },
            {
                "bytes": ""
            }
        ]
    }


@pytest.fixture
def bad_vault_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "bytes": ""
            },
            {
                "bytes": ""
            }
        ]
    }


@pytest.fixture
def good_oracle_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "constructor": 2,
                "fields": [
                    {
                        "map": [
                            {
                                "k": {
                                    "int": 0
                                },
                                "v": {
                                    "int": 2737
                                }
                            },
                            {
                                "k": {
                                    "int": 1
                                },
                                "v": {
                                    "int": 1722379126784
                                }
                            },
                            {
                                "k": {
                                    "int": 2
                                },
                                "v": {
                                    "int": 1722380926784
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def bad_oracle_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "constructor": 2,
                "fields": [
                    {
                        "map": [
                            {
                                "k": {
                                    "int": 0
                                },
                                "v": {
                                    "int": 2737
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def good_reference_datum():
    return {
        "constructor": 0,
        "fields": [
            {
                "bytes": "f4a78bbff6d5e7e492915986abc495382247af659018451a25cec92c"
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "list": [
                            {
                                "bytes": "d858ecf3e73e18bef8383a16e856778e033cfd1c8867c70dc9b68b42"
                            },
                            {
                                "bytes": "10a20db9464d89dab407b3397e67facf83db8d442e601b627c0a351f"
                            },
                            {
                                "bytes": "121ce13907d40c7a598d182ed751d39279cf30d50decb17151b3a587"
                            }
                        ]
                    },
                    {
                        "int": 2
                    }
                ]
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "1e3105f23f2ac91b3fb4c35fa4fe301421028e356e114944e902005b"
                    },
                    {
                        "constructor": 0,
                        "fields": [
                            {
                                "bytes": "8f7b0ce283a92df9a3b69ac0b8f10d8bc8bcf8fbd1fe72596ee8bd6c"
                            },
                            {
                                "bytes": ""
                            }
                        ]
                    }
                ]
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "2ca10dd441432b28e5b4cfb387474aa95bcfbdc43628e78e6663ba24"
                    },
                    {
                        "bytes": "5077cd70ad643a3f8b1aa2330c54959eada48ee37f2809399a25f2f9"
                    },
                    {
                        "bytes": "0809eab9ec51e7f6233309998d9a29e9f865cf5ea4e3b048adccb686"
                    },
                    {
                        "bytes": "f5a76a47d658b09b0a29909c5397caf7b4d70f1b0de8f5b5f1ebe8cb"
                    },
                    {
                        "bytes": "e9ca90e86eb6923bb3bda252b15e327d69c4321cf5d832f74b61c7a9"
                    }
                ]
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "int": 1000000
                    },
                    {
                        "int": 1000000
                    },
                    {
                        "int": 1000000
                    }
                ]
            },
            {
                "bytes": "ed37d8a9be7f2e99db9d973731f63e9afc74b99b436e161390f907c5"
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "e4d33c4f86ac40278cdd80572abfa7e91b01fbba68d8fa258bf7ef46"
                    },
                    {
                        "bytes": "916c03c8f98c44a176de6660e6e45ac0cd59aa4fe6c332bed1e8d79d"
                    },
                    {
                        "list": [
                            {
                                "bytes": "44618a67"
                            },
                            {
                                "bytes": "45b555bd"
                            },
                            {
                                "bytes": "4cae2fd2"
                            },
                            {
                                "bytes": "57d8ea10"
                            },
                            {
                                "bytes": "5f3a83b8"
                            },
                            {
                                "bytes": "6aa8bd5d"
                            },
                            {
                                "bytes": "726aaa90"
                            },
                            {
                                "bytes": "8be2ee9c"
                            },
                            {
                                "bytes": "8c4234e8"
                            },
                            {
                                "bytes": "d05fd9e2"
                            },
                            {
                                "bytes": "ecf39067"
                            },
                            {
                                "bytes": "0892f565"
                            },
                            {
                                "bytes": "0c55ccd7"
                            },
                            {
                                "bytes": "3d4d9807"
                            },
                            {
                                "bytes": "520fc569"
                            },
                            {
                                "bytes": "5c99b6b4"
                            },
                            {
                                "bytes": "63e2123b"
                            },
                            {
                                "bytes": "78820b6c"
                            },
                            {
                                "bytes": "a16af814"
                            },
                            {
                                "bytes": "ad997a92"
                            },
                            {
                                "bytes": "e7982636"
                            }
                        ]
                    },
                    {
                        "bytes": "d4add3a85c2ced3607ba0b17e71a403863c2435348bba0821f74523a"
                    }
                ]
            },
            {
                "constructor": 0,
                "fields": [
                    {
                        "bytes": "b07d22a4dc75abdba1b8c80033a15b85305b76521a0114b17f291a87"
                    },
                    {
                        "bytes": "362e3f869c98ce971ead0e2705c56df467ddd2aecb44f6f216c3e1d5"
                    },
                    {
                        "bytes": "4f7261636c6546656564"
                    },
                    {
                        "bytes": "769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff"
                    },
                    {
                        "bytes": "744e45574d"
                    },
                    {
                        "int": 500000000000
                    }
                ]
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


def test_is_good_vault_datum_valid(good_vault_datum):
    result = vault_validity(good_vault_datum)
    assert result is True


def test_is_bad_vault_datum_valid(bad_vault_datum):
    result = vault_validity(bad_vault_datum)
    assert result is False


def test_is_good_oracle_datum_valid(good_oracle_datum):
    result = oracle_validity(good_oracle_datum)
    assert result is True


def test_is_bad_oracle_datum_valid(bad_oracle_datum):
    result = oracle_validity(bad_oracle_datum)
    assert result is False


def test_is_good_data_datum_valid(good_reference_datum):
    result = data_validity(good_reference_datum)
    assert result is True
