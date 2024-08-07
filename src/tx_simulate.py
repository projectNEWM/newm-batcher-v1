"""
Fork of https://github.com/logicalmechanism/tx_simulation
NEWM Batcher can not use Koios so only the workable parts are going to
be used inside the batcher.
"""
import json
import os
import subprocess
import tempfile

import cbor2


def sort_lexicographically(*args: str) -> list[str]:
    """
    Sorts the function inputs in lexicographical order.

    Args:
    *args: Strings to be sorted.

    Returns:
    A list of strings sorted in lexicographical order.
    """
    return sorted(args)


def get_index_in_order(ordered_list: list[str], item: str) -> int:
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
        return None


def to_bytes(s: str) -> bytes:
    """ Convert the string to bytes and prepend with 'h' to indicate hexadecimal format.
    The bytes representation will be returned else a ValueError is raised.

    Args:
        s (str): The hexadecimal string used in byte conversion

    Returns:
        bytes: A bytestring in proper cbor format.
    """
    try:
        return bytes.fromhex(s)
    except ValueError:
        raise ValueError(
            "non-hexadecimal number found in fromhex() arg at position 1")


def resolve_inputs(tx_cbor: str) -> list[tuple[str, int]]:
    """Resolves the inputs from the tx cbor.

    Args:
        tx_cbor (str): The transaction cbor

    Returns:
        list[tuple[str, int]]: A list of tuples of the utxo inputs.
    """
    # resolve the data from the cbor
    data = cbor2.loads(bytes.fromhex(tx_cbor))

    # we just need the body here
    txBody = data[0]

    # all the types of inputs; tx inputs, collateral, and reference
    inputs = txBody[0] + txBody[13] + txBody[18]

    # convert into list of tuples
    inputs = [(utxo[0].hex(), int(utxo[1])) for utxo in inputs]

    return inputs


def get_cbor_from_file(tx_draft_path: str) -> str:
    # get cborHex from tx draft
    with open(tx_draft_path, 'r') as file:
        data = json.load(file)

    try:
        # get cbor hex from the file and proceed
        return data['cborHex']
    except KeyError:
        return None


def inputs_from_cbor(cborHex: str) -> tuple[str, str] | None:
    """Given a tx draft file return the inputs in lexicographical order and the tx cbor required
    for tx simulation.

    Args:
        tx_draft_path (str): The path to the tx.draft file
        network (bool): The network flag, mainnet (True) or preprod (False)
        debug (bool, optional): Debug prints to console. Defaults to False.

    Returns:
        tuple[str, str] | None: Returns the inputs and inputs cbor or None
    """
    # resolve the inputs
    inputs = resolve_inputs(cborHex)
    # prepare inputs for cbor dumping
    prepare_inputs = [(to_bytes(txin[0]), txin[1]) for txin in inputs]
    # we need the cbor hex here of the inputs
    inputs_cbor = cbor2.dumps(prepare_inputs).hex()
    return inputs, inputs_cbor


def simulate(tx_cbor: str, input_cbor: str, output_cbor: str, network: bool = False, debug: bool = False) -> list[dict]:
    # try to simulate the tx and return the results else return an empty dict
    try:

        # use some temp files that get deleted later
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_tx_file:
            temp_tx_file.write(tx_cbor)
            temp_tx_file_path = temp_tx_file.name
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_input_file:
            temp_input_file.write(input_cbor)
            temp_input_file_path = temp_input_file.name
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_output_file:
            temp_output_file.write(output_cbor)
            temp_output_file_path = temp_output_file.name

        # aiken must be on path
        func = [
            'aiken', 'tx', 'simulate',
            temp_tx_file_path,
            temp_input_file_path,
            temp_output_file_path
        ]

        # this is calculated from the block after the hf on preprod
        if network is False:
            func += [
                '--zero-time', '1655769600000',
                '--zero-slot', '86400',
            ]

        # run the function, get output from console if debug is True
        output = subprocess.run(
            func,
            check=True,
            capture_output=False if debug is True else True,
            text=True
        )

        # this should remove the temp files
        os.remove(temp_tx_file_path)
        os.remove(temp_input_file_path)
        os.remove(temp_output_file_path)

        # if debug is on then dont load the json
        if debug is False:
            return json.loads(output.stdout)
        else:
            # in debug mode it will assume to be failed
            return [{}]

    except subprocess.CalledProcessError:
        # the simulation failed in some way
        return [{}]
