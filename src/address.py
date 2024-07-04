from pycardano import Address, Network, VerificationKeyHash


def from_pkh_sc(pkh: str, sc: str, network: Network) -> str:
    """
    Generates an bech32 address from a payment key hash (pkh) and an optional staking key hash (sc).

    Args:
        pkh (str): The payment key hash as a hexadecimal string.
        sc (str): The staking key hash as a hexadecimal string.
        network (Network): The network flag.

    Returns:
        str: The encoded address.
    """
    vkh = VerificationKeyHash(bytes.fromhex(pkh))
    # the wallet type assumes empty stake credentials are enterprise addresses
    if sc == "":
        return Address(payment_part=vkh, network=network).encode()
    else:
        kh = VerificationKeyHash(bytes.fromhex(sc))
        return Address(payment_part=vkh, staking_part=kh, network=network).encode()
