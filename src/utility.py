import hashlib
import os


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