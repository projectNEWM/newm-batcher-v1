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
