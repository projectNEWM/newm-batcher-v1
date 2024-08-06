import pytest
from cbor2 import dumps

from src.cbor import convert_datum, dumps_with_indefinite_array, tag, to_bytes


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
                        "bytes": "772f3133e1c6441496953066aec4450696d6b7039c1b4b7305679223"
                    },
                    {
                        "bytes": "190345c27c9190aee63d7babc4d4e6044c95ca8c2b9ec6e7dff6c40f"
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
                        "bytes": "36bd690356f3dfd216c6cf0aba028f5626a0802e6f898f36c78bd682"
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
                                    "int": 1937
                                }
                            },
                            {
                                "k": {
                                    "int": 1
                                },
                                "v": {
                                    "int": 1722885782626
                                }
                            },
                            {
                                "k": {
                                    "int": 2
                                },
                                "v": {
                                    "int": 1722887582626
                                }
                            }
                        ]
                    }
                ]
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
                        "bytes": "dfff8bc9cdfa7eb004eab6c303984b8e7b6f7cf3337f17826a23c1e2"
                    },
                    {
                        "bytes": "001bc28000a5125631842958ab17da111bd82c01543c84083fed0be251a821a2"
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
                        "bytes": "555344"
                    },
                    {
                        "bytes": ""
                    },
                    {
                        "int": 10000000
                    }
                ]
            },
            {
                "int": 100000000
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
                "bytes": "ca11ab1e004e15abe6809d452911117376b1f8cc0515e8f587ed5e6c13556ec2"
            }
        ]
    }


def test_empty_datum():
    result = dumps(tag(121, [])).hex()
    assert result == "d87980"


def test_input_list():
    inputs = [
        ["4F456C9F7D6EB3D1550B4E5A1BBD7BB2C779A826E1CB393FD17EA1D735799E71", 1],
        ["4F456C9F7D6EB3D1550B4E5A1BBD7BB2C779A826E1CB393FD17EA1D735799E71", 4],
        ["779FFADAAEB39AECB6837C34DB101B1AF61A0E00C522FF7B4720FA8003587D89", 0],
        ["66991B37B2F4812170261C9C9AB2B02C9748C9882DEC48A9C14A73310CCC2712", 1],
    ]
    prepare_inputs = [(to_bytes(txin[0]), txin[1]) for txin in inputs]
    input_cbor = dumps(prepare_inputs).hex()
    assert input_cbor == "848258204f456c9f7d6eb3d1550b4e5a1bbd7bb2c779a826e1cb393fd17ea1d735799e71018258204f456c9f7d6eb3d1550b4e5a1bbd7bb2c779a826e1cb393fd17ea1d735799e7104825820779ffadaaeb39aecb6837c34db101b1af61a0e00c522ff7b4720fa8003587d890082582066991b37b2f4812170261c9c9ab2b02c9748c9882dec48a9c14a73310ccc271201"


def test_wallet_type():
    datum = {
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
    fields = [to_bytes(value['bytes']) for value in datum["fields"]]
    result = dumps_with_indefinite_array(121 + datum["constructor"], fields).hex()
    assert result == "d8799f581ce154dbd9ee8685258d7be1d3f374e4c2f1aebeada68707113b1422b040ff"


def test_token_type():
    datum = {
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
    }
    fields = []
    for value in datum['fields']:
        if 'bytes' in value:
            fields.append(to_bytes(value['bytes']))
        if 'int' in value:
            fields.append(value['int'])
    result = dumps_with_indefinite_array(121 + datum["constructor"], fields).hex()
    assert result == "d8799f581c769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff45744e45574d1a000f4240ff"


def test_queue_datum_to_cbor(good_queue_datum):
    answer = "d8799fd8799f581c0d28d4a2e4c1504b8bf77f7db89561ca6421eef8ee1ea5a99300e88e40ff1a0012d687d8799f581c769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff45744e45574d1a000f4240ff5820ca11ab1e004e15abe6809d452911117376b1f8cc0515e8f587ed5e6c13556ec2ff"
    result = convert_datum(good_queue_datum)
    assert result.hex() == answer


def test_sale_datum_to_cbor(good_sale_datum):
    answer = "d8799fd8799f581c39f29cfe6ab0765578a6e0d8871e1a3bc18f5d277b257095aabf1cd840ffd8799f581cdfff8bc9cdfa7eb004eab6c303984b8e7b6f7cf3337f17826a23c1e25820001bc28000a5125631842958ab17da111bd82c01543c84083fed0be251a821a201ffd8799f43555344401a00989680ff1a05f5e100ff"
    result = convert_datum(good_sale_datum)
    assert result.hex() == answer


def test_vault_datum_to_cbor(good_vault_datum):
    answer = "d8799f581ce154dbd9ee8685258d7be1d3f374e4c2f1aebeada68707113b1422b040ff"
    result = convert_datum(good_vault_datum)
    assert result.hex() == answer


def test_oracle_datum_to_cbor(good_oracle_datum):
    answer = "d8799fd87b9fa300190791011b0000019123febc62021b00000191241a33a2ffff"
    result = convert_datum(good_oracle_datum)
    assert result.hex() == answer


def test_data_datum_to_cbor(good_reference_datum):
    answer = "d8799f581cf4a78bbff6d5e7e492915986abc495382247af659018451a25cec92cd8799f9f581cd858ecf3e73e18bef8383a16e856778e033cfd1c8867c70dc9b68b42581c10a20db9464d89dab407b3397e67facf83db8d442e601b627c0a351f581c121ce13907d40c7a598d182ed751d39279cf30d50decb17151b3a587ff02ffd8799f581c1e3105f23f2ac91b3fb4c35fa4fe301421028e356e114944e902005bd8799f581c8f7b0ce283a92df9a3b69ac0b8f10d8bc8bcf8fbd1fe72596ee8bd6c40ffffd8799f581c2ca10dd441432b28e5b4cfb387474aa95bcfbdc43628e78e6663ba24581c772f3133e1c6441496953066aec4450696d6b7039c1b4b7305679223581c190345c27c9190aee63d7babc4d4e6044c95ca8c2b9ec6e7dff6c40f581cf5a76a47d658b09b0a29909c5397caf7b4d70f1b0de8f5b5f1ebe8cb581ce9ca90e86eb6923bb3bda252b15e327d69c4321cf5d832f74b61c7a9ffd8799f1a000f42401a000f42401a000f4240ff581ced37d8a9be7f2e99db9d973731f63e9afc74b99b436e161390f907c5d8799f581ce4d33c4f86ac40278cdd80572abfa7e91b01fbba68d8fa258bf7ef46581c916c03c8f98c44a176de6660e6e45ac0cd59aa4fe6c332bed1e8d79d9f4444618a674445b555bd444cae2fd24457d8ea10445f3a83b8446aa8bd5d44726aaa90448be2ee9c448c4234e844d05fd9e244ecf39067440892f565440c55ccd7443d4d980744520fc569445c99b6b44463e2123b4478820b6c44a16af81444ad997a9244e7982636ff581c36bd690356f3dfd216c6cf0aba028f5626a0802e6f898f36c78bd682ffd8799f581cb07d22a4dc75abdba1b8c80033a15b85305b76521a0114b17f291a87581c362e3f869c98ce971ead0e2705c56df467ddd2aecb44f6f216c3e1d54a4f7261636c6546656564581c769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff45744e45574d1b000000746a528800ffff"
    result = convert_datum(good_reference_datum)
    assert result.hex() == answer
