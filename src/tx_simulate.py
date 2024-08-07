"""
Fork of https://github.com/logicalmechanism/tx_simulation
NEWM Batcher can not use Koios so only the workable parts are going to
be used inside the batcher.
"""


def sort_lexicographically(*args):
    """
    Sorts the function inputs in lexicographical order.

    Args:
    *args: Strings to be sorted.

    Returns:
    A list of strings sorted in lexicographical order.
    """
    return sorted(args)


def get_index_in_order(ordered_list, item):
    """
    Returns the index of the given item in the ordered list.

    Args:
    ordered_list: A list of strings sorted in lexicographical order.
    item: The string whose index is to be found.

    Returns:
    The index of the item in the ordered list.
    """
    try:
        return ordered_list.index(item)
    except ValueError:
        return -1  # Return -1 if the item is not found
