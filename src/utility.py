import binascii
import hashlib
import os
import time


def sha3_256(input_string: str) -> str:
    """
    Compute the hex digest of a sha3_256 hash of some input string.

    Args:
        input_string (str): Some input string to be hashed.

    Returns:
        str: The sha3_256 hash of some string.
    """
    # Calculate the SHA3-256 hash
    return hashlib.sha3_256(str(input_string).encode('utf-8')).hexdigest()


def create_folder_if_not_exists(folder_path: str) -> None:
    """
    Creates a folder if and only if it does not already exist.

    Args:
        folder_path (str): The path to the folder
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def parent_directory_path() -> str:
    """
    Return the parent directory path

    Returns:
        str: The parent path
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def file_exists(file_path):
    """
    Check if a file exists at the given file_path.

    Args:
    - file_path (str): The path to the file to check.

    Returns:
    - bool: True if the file exists, False otherwise.
    """
    return os.path.exists(file_path)


def find_index_of_target(lst: list[tuple[str, int]], target: str) -> int | None:
    """
    Finds the index of a target tuple in a list of tuples.

    Parameters:
    lst (List[Tuple[str, int]]): The list of tuples to search.
    target (str): The target string in the format 'hash#index'.

    Returns:
    Optional[int]: The index of the target tuple if found, otherwise None.
    """
    # Split the target string into the hash and index
    target_hash, target_index = target.split('#')
    target_index = int(target_index)  # Convert the index part to an integer

    # Create the target tuple
    target_tuple = (target_hash, target_index)

    # Find the index of the target tuple in the list
    if target_tuple in lst:
        return lst.index(target_tuple)
    else:
        return None  # Return None if the target is not found


def current_time() -> int:
    """Current unix time in milliseconds.

    Returns:
        int: The integer value of unix time.
    """
    return int(1000 * time.time())


def get_first_line(file_path: str) -> str:
    """Get the first line from some file.

    Args:
        file_path (str): The file path to get the line.

    Returns:
        str: The string in the file.
    """
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
    return first_line


def generate_token_name(tx_id: str, tx_idx: int, prefix: str) -> str:
    """Generates a token name following the assist library standard.

    Args:
        tx_id (str): The transaction id
        tx_idx (int): The transaction index
        prefix (str): The token prefix. This may be an empty string

    Returns:
        str: The token name.
    """
    tx_id_bytes = binascii.unhexlify(tx_id)
    # use sha3_256 to hex the bytes of tx id
    hash_func = hashlib.new('sha3_256')
    hash_func.update(tx_id_bytes)
    tx_id_hash = hash_func.hexdigest()
    # we need the index in hex form but without x as the odd digit
    tx_idx_hex = hex(tx_idx)[-2:]
    # if it exists then replace with 0
    if "x" in tx_idx_hex:
        tx_idx_hex = tx_idx_hex.replace("x", "0")
    # smash it together then trim the first 64 characters
    tx_id = prefix + tx_idx_hex + tx_id_hash
    return tx_id[0:64]


def generate_token_string(tokens: dict) -> str:
    """Generates a cardano-cli friend token string of the form `quantity policy_id.token_name`.

    Args:
        tokens (dict): The token dictionary from the utxo.

    Returns:
        str: The token string.
    """
    string = ""
    for pid in tokens:
        if pid == "lovelace":
            continue
        for tkn in tokens[pid]:
            token = f"{tokens[pid][tkn]} {pid}.{tkn}"
            if string == "":
                string += token
            else:
                string += " + " + token
    return string
