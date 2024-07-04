import json


def read(file_name: str) -> dict:
    """Take in a file name and load the json from the file.

    Args:
        file_name (str): File name and path

    Returns:
        dict: The data from json file
    """
    with open(file_name, 'r') as f:
        d = json.load(f)
    return d


def write(data: dict, file_name: str) -> None:
    """Take in some data and dump it into some json file inside tmp.

    Args:
        data (dict): The data dictionary
        file_name (str): File name and path
    """
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)
