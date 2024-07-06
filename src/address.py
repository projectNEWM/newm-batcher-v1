from pycardano import Address, Network, VerificationKeyHash


def from_pkh_sc(pkh: str, sc: str, network: Network) -> str:
    """
    Generates a bech32 address from a payment key hash (pkh) and an optional staking key hash (sc).

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


def pkh_from_address(addr: str) -> str:
    """
    Get the public key hash from a bech32 address.

    Args:
        addr (str): The address

    Returns:
        str: The public key hash
    """
    address = Address.from_primitive(addr)
    pkh = address.payment_part
    return pkh.to_primitive().hex()
