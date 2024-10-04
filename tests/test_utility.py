from src.utility import find_index_of_target, generate_token_name, sha3_256


def test_empty_string_hash():
    result = sha3_256("")
    assert result == "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"


def test_ascii_string_hash():
    result = sha3_256("Hello, World!")
    assert result == "1af17a664e3fa8e419b8ba05c2a173169df76162a5a286e0c405b460d478f7ef"


def test_hex_string_hash():
    result = sha3_256("acab")
    assert result == "0ec4297a959eae9cba7160d763b4f41f6878bf180b358016c8f7bffcc93c2757"


def test_find_index():
    # Example usage
    lst = [
        ('2b38bb57ceb66a8eadd99540df564b14181894a8a4c964fe5f38342cd58a0a08', 0),
        ('451656c07cbc67f492eabd3bab41299fb50a441cabe73c6c5391ec703eed84f7', 0),
        ('b9ed89b0664d79b6b8c73c8a7341c21dfccb9a9ee30bb0d375f6686d28bc56e6', 0),
        ('ca7ff0366ffd073bcd565b34eec070ed82d0314b1779d99edec49fced6ed698a', 0),
        ('1e0b413409dd9591b2a69bca80d7d776e8bb5130f02af0bf886e08ce5b6e183a', 0),
        ('098a3281a90809d9ee1df32efb2570fce45dab43894e4509181a05cee8a23e18', 1),
        ('8678bdfd35e12789266847ee3e90c289509fc8f359b685b99371252690c4433d', 1),
        ('8c3d025bdd3c8bb4e5b3806f2b148a64ac0640597019960ace09ac8423d4ca89', 0),
        ('9af67c86e6137d41915c0d0e554ad69ee86911c4c4d4f68fd0a2f4d384673ca9', 1),
        ('d784249b5093460ad0e3ae9e57d80c5651e3046c029f091fd980f0b997e6ddba', 1)
    ]

    target = 'ca7ff0366ffd073bcd565b34eec070ed82d0314b1779d99edec49fced6ed698a#0'

    # Find and print the index
    index = find_index_of_target(lst, target)
    assert index == 3


def test_cant_find_index():
    # Example usage
    lst = [
        ('2b38bb57ceb66a8eadd99540df564b14181894a8a4c964fe5f38342cd58a0a08', 0),
        ('451656c07cbc67f492eabd3bab41299fb50a441cabe73c6c5391ec703eed84f7', 0),
        ('b9ed89b0664d79b6b8c73c8a7341c21dfccb9a9ee30bb0d375f6686d28bc56e6', 0),
        ('ca7ff0366ffd073bcd565b34eec070ed82d0314b1779d99edec49fced6ed698a', 0),
        ('1e0b413409dd9591b2a69bca80d7d776e8bb5130f02af0bf886e08ce5b6e183a', 0),
        ('098a3281a90809d9ee1df32efb2570fce45dab43894e4509181a05cee8a23e18', 1),
        ('8678bdfd35e12789266847ee3e90c289509fc8f359b685b99371252690c4433d', 1),
        ('8c3d025bdd3c8bb4e5b3806f2b148a64ac0640597019960ace09ac8423d4ca89', 0),
        ('9af67c86e6137d41915c0d0e554ad69ee86911c4c4d4f68fd0a2f4d384673ca9', 1),
        ('d784249b5093460ad0e3ae9e57d80c5651e3046c029f091fd980f0b997e6ddba', 1)
    ]

    target = 'da7ff0366ffd073bcd565b34eec070ed82d0314b1779d99edec49fced6ed698a#0'

    # Find and print the index
    index = find_index_of_target(lst, target)
    assert index is None


def test_generate_name_from_empty_strings():
    assert generate_token_name("ab69aab2efe96149ca2fc045f8cdfadaa2213e5f71f7f427632ac1216bd6106d", 0, "000643b0") == "000643b00001f1ca8bb6ed0bd798019448bf8b5b9a539958477b53fd86c6d27e"
