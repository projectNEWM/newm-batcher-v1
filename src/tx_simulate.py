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

from src.address import bech32_to_hex
from src.cbor import convert_datum, tag, to_bytes
from src.ogmios import ogmios_simulate
from src.utility import find_index_of_target
from src.utxo_manager import UTxOManager


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
    inputs = list(txBody[0]) + list(txBody[13]) + list(txBody[18])

    # convert into list of tuples
    inputs = [(utxo[0].hex(), int(utxo[1])) for utxo in inputs]

    # return sorted(inputs)
    return inputs


def get_cbor_from_file(tx_draft_path: str) -> str:
    """Open the transaction draft file and return the cbor hex.

    Args:
        tx_draft_path (str): The path to the draft transaction file.

    Returns:
        str: The cbor of the transaction.
    """
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
    """Simulate a transaction with aiken tx simulate.

    Args:
        tx_cbor (str): The transaction cbor
        input_cbor (str): The proper input cbor.
        output_cbor (str): The proper output cbor in order of the input cbor.
        network (bool, optional): The network flag. Defaults to False.
        debug (bool, optional): The debug flag. Defaults to False.

    Returns:
        list[dict]: The execution units in aiken simulate format.
    """
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


def calculate_total_fee(tx_fee: int, execution_units: list[dict[str, int]]) -> int:
    """Given a set of executions and the tx fee calculate the total fee

    Args:
        tx_fee (int): The tx fee calculated with the cli
        execution_units (list[dict[str, int]]): The list of execution units, order does not matter

    Returns:
        int: The total fee
    """
    priceMemory = 5.77e-2
    priceSteps = 7.21e-5
    computational_fee = 0
    for unit in execution_units:
        computational_fee += unit['cpu'] * \
            priceSteps + unit['mem'] * priceMemory
    return int(tx_fee + computational_fee)


def convert_execution_unit(execution_unit: dict[str, int]) -> str:
    """Place a execution unit in proper cli formatting.

    Args:
        execution_unit (dict[str, int]): The execution units for some process.

    Returns:
        str: The proper cli string formatting for execution units.
    """
    return f"({execution_unit['cpu']}, {execution_unit['mem']})"


def purchase_simulation(cborHex: str, utxo: UTxOManager, config: dict) -> list[dict]:
    """Construct the proper cbor from the cbor hex and the utxo manager and
    simulate the purchase transaction

    Args:
        cborHex (str): The purchase transaction cbor hex.
        utxo (UTxOManager): The utxo manager
        config (dict): The config file

    Returns:
        list[dict]: The execution units in Aiken format.
    """
    inputs, inputs_cbor = inputs_from_cbor(cborHex)

    # initialize the outputs
    outputs = [{} for _ in inputs]

    # build outputs
    # batcher
    batcher_index = find_index_of_target(inputs, utxo.batcher.txid)
    batcher_bytes = to_bytes(bech32_to_hex(config['batcher_address']))
    outputs[batcher_index] = {0: batcher_bytes,
                              1: utxo.batcher.value.simulate_form()}
    # sale
    sale_index = find_index_of_target(inputs, utxo.sale.txid)
    sale_bytes = to_bytes(bech32_to_hex(config['sale_address']))
    sale_datum_bytes = [1, tag(24, convert_datum(utxo.sale.datum))]
    outputs[sale_index] = {
        0: sale_bytes, 1: utxo.sale.value.simulate_form(), 2: sale_datum_bytes}
    # queue
    queue_index = find_index_of_target(inputs, utxo.queue.txid)
    queue_bytes = to_bytes(bech32_to_hex(config['queue_address']))
    queue_datum_bytes = [1, tag(24, convert_datum(utxo.queue.datum))]
    outputs[queue_index] = {
        0: queue_bytes, 1: utxo.queue.value.simulate_form(), 2: queue_datum_bytes}
    # vault
    vault_index = find_index_of_target(inputs, utxo.vault.txid)
    if vault_index is not None:
        vault_bytes = to_bytes(bech32_to_hex(config['vault_address']))
        vault_datum_bytes = [1, tag(24, convert_datum(utxo.vault.datum))]
        outputs[vault_index] = {
            0: vault_bytes, 1: utxo.vault.value.simulate_form(), 2: vault_datum_bytes}
    # oracle
    oracle_index = find_index_of_target(inputs, utxo.oracle.txid)
    if oracle_index is not None:
        oracle_bytes = to_bytes(bech32_to_hex(config['oracle_address']))
        oracle_datum_bytes = [1, tag(24, convert_datum(utxo.oracle.datum))]
        outputs[oracle_index] = {
            0: oracle_bytes, 1: utxo.oracle.value.simulate_form(), 2: oracle_datum_bytes}
    # collateral; hardcoded
    collat_index = find_index_of_target(inputs, config['collat_utxo'])
    collat_bytes = to_bytes(bech32_to_hex(config['collat_address']))
    outputs[collat_index] = {0: collat_bytes, 1: 5000000}
    # data
    data_index = find_index_of_target(inputs, utxo.data.txid)
    data_bytes = to_bytes(bech32_to_hex(config['data_address']))
    data_datum_bytes = [1, tag(24, convert_datum(utxo.data.datum))]
    outputs[data_index] = {
        0: data_bytes, 1: utxo.data.value.simulate_form(), 2: data_datum_bytes}
    # reference stuff
    reference_bytes = to_bytes(bech32_to_hex(config['reference_address']))
    # sale ref
    sale_ref_index = find_index_of_target(inputs, utxo.reference.sale.txid)
    sale_ref_bytes = tag(24, to_bytes(cbor2.dumps(
        [3, to_bytes(utxo.reference.sale.cborHex)]).hex()))
    outputs[sale_ref_index] = {
        0: reference_bytes, 1: utxo.reference.sale.value.simulate_form(), 3: sale_ref_bytes}
    # queue ref
    queue_ref_index = find_index_of_target(inputs, utxo.reference.queue.txid)
    queue_ref_bytes = tag(24, to_bytes(cbor2.dumps(
        [3, to_bytes(utxo.reference.queue.cborHex)]).hex()))
    outputs[queue_ref_index] = {
        0: reference_bytes, 1: utxo.reference.queue.value.simulate_form(), 3: queue_ref_bytes}
    # vault ref
    vault_ref_index = find_index_of_target(inputs, utxo.reference.vault.txid)
    if vault_ref_index is not None:
        vault_ref_bytes = tag(24, to_bytes(cbor2.dumps(
            [3, to_bytes(utxo.reference.vault.cborHex)]).hex()))
        outputs[vault_ref_index] = {
            0: reference_bytes, 1: utxo.reference.vault.value.simulate_form(), 3: vault_ref_bytes}

    outputs_cbor = cbor2.dumps(outputs).hex()

    network = True if "mainnet" in config['network'] else False
    execution_units = simulate(
        cborHex, inputs_cbor, outputs_cbor, network=network, debug=config['debug_mode'])
    return execution_units


def refund_simulation(cborHex: str, utxo: UTxOManager, config: dict) -> list[dict]:
    """Construct the proper cbor from the cbor hex and the utxo manager and
    simulate the refund transaction.

    Args:
        cborHex (str): The refund transaction cbor hex.
        utxo (UTxOManager): The utxo manager
        config (dict): The config file

    Returns:
        list[dict]: The execution units in Aiken format.
    """
    inputs, inputs_cbor = inputs_from_cbor(cborHex)

    # initialize the outputs
    outputs = [{} for _ in inputs]

    # build outputs
    # batcher
    batcher_index = find_index_of_target(inputs, utxo.batcher.txid)
    batcher_bytes = to_bytes(bech32_to_hex(config['batcher_address']))
    outputs[batcher_index] = {0: batcher_bytes,
                              1: utxo.batcher.value.simulate_form()}
    # sale
    sale_index = find_index_of_target(inputs, utxo.sale.txid)
    sale_bytes = to_bytes(bech32_to_hex(config['sale_address']))
    sale_datum_bytes = [1, tag(24, convert_datum(utxo.sale.datum))]
    outputs[sale_index] = {
        0: sale_bytes, 1: utxo.sale.value.simulate_form(), 2: sale_datum_bytes}
    # queue
    queue_index = find_index_of_target(inputs, utxo.queue.txid)
    queue_bytes = to_bytes(bech32_to_hex(config['queue_address']))
    queue_datum_bytes = [1, tag(24, convert_datum(utxo.queue.datum))]
    outputs[queue_index] = {
        0: queue_bytes, 1: utxo.queue.value.simulate_form(), 2: queue_datum_bytes}
    # oracle
    oracle_index = find_index_of_target(inputs, utxo.oracle.txid)
    if oracle_index is not None:
        oracle_bytes = to_bytes(bech32_to_hex(config['oracle_address']))
        oracle_datum_bytes = [1, tag(24, convert_datum(utxo.oracle.datum))]
        outputs[oracle_index] = {
            0: oracle_bytes, 1: utxo.oracle.value.simulate_form(), 2: oracle_datum_bytes}
    # collateral; hardcoded
    collat_index = find_index_of_target(inputs, config['collat_utxo'])
    collat_bytes = to_bytes(bech32_to_hex(config['collat_address']))
    outputs[collat_index] = {0: collat_bytes, 1: 5000000}
    # data
    data_index = find_index_of_target(inputs, utxo.data.txid)
    data_bytes = to_bytes(bech32_to_hex(config['data_address']))
    data_datum_bytes = [1, tag(24, convert_datum(utxo.data.datum))]
    outputs[data_index] = {
        0: data_bytes, 1: utxo.data.value.simulate_form(), 2: data_datum_bytes}

    # reference stuff
    reference_bytes = to_bytes(bech32_to_hex(config['reference_address']))
    # queue ref
    queue_ref_index = find_index_of_target(inputs, utxo.reference.queue.txid)
    queue_ref_bytes = tag(24, to_bytes(cbor2.dumps(
        [3, to_bytes(utxo.reference.queue.cborHex)]).hex()))
    outputs[queue_ref_index] = {
        0: reference_bytes, 1: utxo.reference.queue.value.simulate_form(), 3: queue_ref_bytes}

    # compute the output cbor
    outputs_cbor = cbor2.dumps(outputs).hex()

    network = True if "mainnet" in config['network'] else False
    execution_units = simulate(
        cborHex, inputs_cbor, outputs_cbor, network=network, debug=config['debug_mode'])
    return execution_units


def transaction_simulation_ogmios(cborHex: str, utxo: UTxOManager, config: dict, additionalUTxOSet: list = []):

    # batcher
    batcherSet = {
        "transaction": {
            "id": utxo.batcher.txid.split('#')[0]
        },
        "index": int(utxo.batcher.txid.split('#')[1]),
        "address": config['batcher_address'],
        "value": {
            "ada": {"lovelace": utxo.batcher.value.inner['lovelace']},
            **utxo.batcher.value.remove_lovelace().inner
        }
    }
    additionalUTxOSet.append(batcherSet)
    # sale
    saleSet = {
        "transaction": {
            "id": utxo.sale.txid.split('#')[0]
        },
        "index": int(utxo.sale.txid.split('#')[1]),
        "address": config['sale_address'],
        "value": {
            "ada": {"lovelace": utxo.sale.value.inner['lovelace']},
            **utxo.sale.value.remove_lovelace().inner
        },
        "datum": convert_datum(utxo.sale.datum).hex()
    }
    additionalUTxOSet.append(saleSet)
    # queue
    queueSet = {
        "transaction": {
            "id": utxo.queue.txid.split('#')[0]
        },
        "index": int(utxo.queue.txid.split('#')[1]),
        "address": config['queue_address'],
        "value": {
            "ada": {"lovelace": utxo.queue.value.inner['lovelace']},
            **utxo.queue.value.remove_lovelace().inner
        },
        "datum": convert_datum(utxo.queue.datum).hex()
    }
    additionalUTxOSet.append(queueSet)
    # vault
    vaultSet = {
        "transaction": {
            "id": utxo.vault.txid.split('#')[0]
        },
        "index": int(utxo.vault.txid.split('#')[1]),
        "address": config['vault_address'],
        "value": {
            "ada": {"lovelace": utxo.vault.value.inner['lovelace']},
            **utxo.vault.value.remove_lovelace().inner
        },
        "datum": convert_datum(utxo.vault.datum).hex()
    }
    additionalUTxOSet.append(vaultSet)
    #
    result = ogmios_simulate(cborHex, additionalUTxOSet)
    try:
        data = result['error']['data']['overlappingOutputReferences']
        # Extract (transaction.id, index) pairs from list_to_check
        pairs_to_check = {(item['transaction']['id'], item['index']) for item in data}

        # Filter list_to_remove_from by removing items with (transaction.id, index) in pairs_to_check
        filtered_list = [
            item for item in additionalUTxOSet
            if (item['transaction']['id'], item['index']) not in pairs_to_check
        ]

        # Print the result
        result = ogmios_simulate(cborHex, filtered_list)
    except KeyError:
        pass
    execution_units = []
    try:
        for unit in result['result']:
            execution_units.append({"mem": unit['budget']["memory"], "cpu": unit['budget']["cpu"]})
    except KeyError:
        return [{}]
    return execution_units
