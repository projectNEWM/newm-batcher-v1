from src.utility import sha3_256


def test_empty_string_hash():
    result = sha3_256("")
    assert result == "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"


def test_ascii_string_hash():
    result = sha3_256("Hello, World!")
    assert result == "1af17a664e3fa8e419b8ba05c2a173169df76162a5a286e0c405b460d478f7ef"


def test_hex_string_hash():
    result = sha3_256("acab")
    assert result == "0ec4297a959eae9cba7160d763b4f41f6878bf180b358016c8f7bffcc93c2757"
