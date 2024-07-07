from pycardano import Network

from src.address import from_pkh_sc
from src.allowlist import asset_names, policy_ids, priority
from src.value import Value


def queue_validity(datum: dict) -> bool:
    """
    Validate that the queue datum is in the correct form for an order to be fulfilled.

    Args:
        datum (dict): The queue datum

    Returns:
        bool: True if valid else False
    """
    try:
        # there are four fields in the datum
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


def incentive_to_value(datum: dict) -> Value:
    incentive = {
        datum['fields'][2]['fields'][0]['bytes']: {
            datum['fields'][2]['fields'][1]['bytes']: datum['fields'][2]['fields'][2]['int']
        }
    }
    return Value(incentive)


def get_incentive_amount(datum: dict) -> tuple[int, int]:
    try:
        return datum['fields'][2]['fields'][2]['int'], priority[datum['fields'][2]['fields'][0]['bytes']]
    except KeyError:
        return None


def get_bundle_amount(datum: dict) -> int:
    try:
        return datum['fields'][1]['int']
    except KeyError:
        return None


def sale_validity(datum: dict) -> bool:
    """
    Validate that the sale datum is in the correct form for an order to be fulfilled.

    Args:
        datum (dict): The sale datum

    Returns:
        bool: True if valid else False
    """
    try:
        # there are four fields in the datum
        if len(datum['fields']) != 4:
            return False

        # wallet check
        if len(datum['fields'][0]['fields']) != 2:
            return False
        if len(datum['fields'][0]['fields'][0]['bytes']) != 56:
            return False
        if len(datum['fields'][0]['fields'][1]['bytes']) not in [0, 56]:
            return False

        # bundle check
        if len(datum['fields'][1]['fields']) != 3:
            return False
        if datum['fields'][1]['fields'][2]['int'] <= 0:
            return False

        # cost check
        if len(datum['fields'][2]['fields']) != 3:
            return False
        if datum['fields'][2]['fields'][2]['int'] <= 0:
            return False

        # bundle size check
        if datum['fields'][3]['int'] <= 0:
            return False

        # every thing seems good
        return True

    except KeyError:
        return False


def bundle_to_value(datum: dict) -> Value:
    bundle = {
        datum['fields'][1]['fields'][0]['bytes']: {
            datum['fields'][1]['fields'][1]['bytes']: datum['fields'][1]['fields'][2]['int']
        }
    }
    return Value(bundle)


def cost_to_value(datum: dict) -> Value:
    cost = {
        datum['fields'][2]['fields'][0]['bytes']: {
            datum['fields'][2]['fields'][1]['bytes']: datum['fields'][2]['fields'][2]['int']
        }
    }
    return Value(cost)


def get_number_of_bundles(queue_datum: dict, sale_datum: dict, sale_value: Value) -> int:
    wanted_bundle_size = queue_datum['fields'][1]['int']
    current_bundle_amt = sale_value.get_quantity(sale_datum['fields'][1]['fields'][0]['bytes'], sale_datum['fields'][1]['fields'][1]['bytes'])
    bundle_amt = sale_datum['fields'][1]['fields'][2]['int']
    if current_bundle_amt // bundle_amt < wanted_bundle_size:
        return current_bundle_amt // bundle_amt
    else:
        return wanted_bundle_size


def to_address(datum: dict, network) -> str:
    try:
        return from_pkh_sc(
            datum['fields'][0]['fields'][0]['bytes'],
            datum['fields'][0]['fields'][1]['bytes'],
            Network.TESTNET if "testnet" in network else Network.MAINNET
        )
    except KeyError:
        return ''
