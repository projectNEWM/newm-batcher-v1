from src.allowlist import asset_names, policy_ids, priority


def queue_validity(datum: dict) -> bool:
    """
    Validate that teh queue datum is in the correct form for an order to be fulfilled.

    Args:
        datum (dict): The queue datum

    Returns:
        bool: True if valid else False
    """
    try:
        # there are four fields in the queue datum
        if len(datum['fields']) != 4:
            return False

        # wallet check
        if len(datum['fields'][0]['fields']) != 2:
            return False
        if len(datum['fields'][0]['fields'][0]['bytes']) != 56:
            return False
        if len(datum['fields'][0]['fields'][1]['bytes']) not in [0, 56]:
            return False

        # bundle size check
        if datum['fields'][1]['int'] <= 0:
            return False

        # incentive check
        if len(datum['fields'][2]['fields']) != 3:
            return False
        if datum['fields'][2]['fields'][0]['bytes'] not in policy_ids:
            return False
        if datum['fields'][2]['fields'][1]['bytes'] not in asset_names:
            return False
        if datum['fields'][2]['fields'][2]['int'] <= 0:
            return False

        # pointer token check
        if len(datum['fields'][3]['bytes']) != 64:
            return False

        # every thing seems good
        return True

    except KeyError:
        # some field doesnt exist
        return False


def get_incentive_amount(datum: dict) -> tuple[int, int]:
    try:
        return datum['fields'][2]['fields'][2]['int'], priority[datum['fields'][2]['fields'][0]['bytes']]
    except KeyError:
        return None
