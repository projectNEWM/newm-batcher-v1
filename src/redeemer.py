def empty(index: int) -> dict:
    """
    Creates the empty datum with a specific index

    Args:
        index (int): The constructor index

    Returns:
        dict: The empty redeemer structure with a specific index.
    """

    # standard empty structure
    data = {
        "constructor": index,
        "fields": []
    }
    return data


def token(pid: str, tkn: str, amt: int) -> dict:
    return {
        "constructor": 0,
        "fields": [
            {
                "bytes": pid
            },
            {
                "bytes": tkn
            },
            {
                "int": amt
            }
        ]
    }


def tokens(token_list: list) -> dict:
    return {
        "constructor": 0,
        "fields": [
            {
                "list": token_list
            }
        ]
    }
