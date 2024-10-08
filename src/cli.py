import datetime
import json
import subprocess
import sys


def query_ref_script_size(socket: str, network: str, inputs: list[str], cli_path: str) -> int:
    func = [
        cli_path,
        'conway',
        'query',
        'ref-script-size',
        '--socket-path',
        socket,
        '--output-json'
    ]
    func += network.split(" ")
    for i in inputs:
        func += ['--tx-in', i]

    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()

    # # exit application if node is not live
    if "Connection refused" in errors.decode() or "Invalid argument" in errors.decode() or "Missing" in errors.decode():
        sys.exit(1)

    json_dict = json.loads(output.decode('utf-8'))
    return json_dict['refInputScriptSize']


def calculate_min_fee(tx_body_file: str, protocol_params_file: str, cli_path: str, script_sizes: int = 0) -> int:
    func = [
        cli_path,
        'conway',
        'transaction',
        'calculate-min-fee',
        '--tx-body-file',
        tx_body_file,
        '--protocol-params-file',
        protocol_params_file,
        '--output-json',
        '--witness-count', '3',
        '--reference-script-size', str(script_sizes)
    ]
    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = p.communicate()
    json_dict = json.loads(output.decode('utf-8'))
    return json_dict['fee']


def does_utxo_exist(socket: str, txin: str, network: str, cli_path: str) -> bool:
    """Query if a utxo exists given network and txin, id#idx.

    Args:
        socket (str): The node socket path
        txin (str): The txin in the form id#idx
        network (str): The network flag

    Returns:
        bool: If the utxo exists then true else false
    """
    func = [
        cli_path,
        'conway',
        'query',
        'utxo',
        '--socket-path',
        socket,
        '--output-json',
        '--tx-in',
        txin
    ]
    func += network.split(" ")
    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()

    # exit application if node is not live
    if "Connection refused" in errors.decode():
        sys.exit(1)

    # Parse the JSON string into a Python dictionary
    json_dict = json.loads(output.decode('utf-8'))
    return len(json_dict) != 0


def query_slot_number(socket: str, unix_time: int, network: str, cli_path: str, delta: int = 0) -> int:
    """Query the slot number for a given network and a given unix time.

    Args:
        socket (str): The node socket path
        unix_time (int): The unix timestamp
        network (str): The network flag
        delta (int | optional): The delta to be added to the unix time

    Returns:
        int: The slot cooresponding to the unix timestamp
    """
    timestamp = datetime.datetime.fromtimestamp((unix_time / 1000) + delta, tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    func = [
        cli_path,
        'conway',
        'query',
        'slot-number',
        '--socket-path',
        socket
    ]
    func += network.split(" ")
    func += [timestamp]
    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    # exit application if node is not live
    if "Connection refused" in errors.decode():
        sys.exit(1)
    # decode output into int
    return int(output.decode())


def query_protocol_parameters(socket: str, file_path: str, network: str, cli_path: str) -> None:
    """Query the protocol parameters for a given network.

    Args:
        socket (str): The node socket path
        file_path (str): The output file path
        network (str): The network flag
    """
    func = [
        cli_path,
        'conway',
        'query',
        'protocol-parameters',
        '--socket-path',
        socket,
        '--out-file',
        file_path
    ]
    func += network.split(" ")

    # this saves to out file
    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, errors = p.communicate()

    # exit application if node is not live
    if "Connection refused" in errors.decode():
        sys.exit(1)


def query_tx_mempool(socket: str, tx_id: str, file_path: str, network: str, cli_path: str) -> None:
    """
    Query the tx mempool and check if a specific transaction exists inside of it.

    Args:
        socket (str): The node socket path
        tx_id (str): The transaction id
        file_path (str): The output file path
        network (str): The network flag
    """
    func = [
        cli_path,
        'conway',
        'query',
        'tx-mempool',
        '--socket-path',
        socket,
        'tx-exists',
        tx_id,
        '--out-file',
        file_path
    ]
    func += network.split(" ")

    # this saves to out file
    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, errors = p.communicate()

    # exit application if node is not live
    if "Connection refused" in errors.decode():
        sys.exit(1)


def does_tx_exists_in_mempool(socket: str, tx_id: str, file_path: str, network: str, cli_path: str) -> bool:
    """
    Query the tx mempool and check if a specific transaction exists inside of it.

    Args:
        socket (str): The node socket path
        tx_id (str): The transaction id
        file_path (str): The output file path
        network (str): The network flag

    Returns:
        bool: If the transaction exists then true else false
    """
    # check the mempool
    query_tx_mempool(socket, tx_id, file_path, network, cli_path)
    # get the block data
    with open(file_path, "r") as read_content:
        data = json.load(read_content)
    return data['exists']


def query_tip(socket: str, file_path: str, network: str, cli_path: str) -> None:
    """
    Query the tip of the blockchain then save to a file.

    Args:
        socket (str): The socket path to the node
        file_path (str): The output file path
        network (str): The network flag
    """
    func = [
        cli_path,
        'conway',
        'query',
        'tip',
        '--socket-path',
        socket,
        '--out-file',
        file_path
    ]
    func += network.split(" ")

    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, errors = p.communicate()

    if "Connection refused" in errors.decode():
        sys.exit(1)


def get_latest_block_number(socket: str, file_path: str, network: str, cli_path: str) -> int:
    """
    Query the tip of the blockchain and returns the latest block number.

    Args:
        socket (str): The socket path to the node
        file_path (str): The output file path
        network (str): The network flag

    Returns:
        int: The latest block number
    """
    # get current tip
    query_tip(socket, file_path, network, cli_path)

    # get the block data
    with open(file_path, "r") as read_content:
        data = json.load(read_content)

    return int(data['block'])


def get_latest_slot_number(socket: str, file_path: str, network: str, cli_path: str) -> int:
    """
    Query the tip of the blockchain and returns the latest block number.

    Args:
        socket (str): The socket path to the node
        file_path (str): The output file path
        network (str): The network flag

    Returns:
        int: The latest block number
    """
    # get current tip
    query_tip(socket, file_path, network, cli_path)

    # get the block data
    with open(file_path, "r") as read_content:
        data = json.load(read_content)

    return int(data['slot'])


def txid(file_path: str, cli_path: str) -> str:
    """
    Get the tx id of a signed transactions.

    Args:
        file_path (str): The transaction file path.

    Returns:
        str: The transaction id
    """
    func = [
        cli_path,
        'conway',
        'transaction',
        'txid',
        '--tx-file',
        file_path
    ]

    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()

    if "Command failed" in errors.decode():
        sys.exit(1)
    return output.decode('utf-8').rstrip()


def sign(draft_file_path: str, signed_file_path: str, network: str, skey_path: str, cli_path: str, collat_path: str = None) -> None:
    """Sign a transaction with a list of payment keys.
    """
    func = [
        cli_path,
        'conway',
        'transaction',
        'sign',
        '--tx-body-file',
        draft_file_path,
        '--tx-file',
        signed_file_path,
        '--signing-key-file',
        skey_path,
    ]
    if collat_path is not None:
        func += [
            '--signing-key-file',
            collat_path,
        ]
    func += network.split(" ")

    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, errors = p.communicate()
    if "Command failed" in errors.decode():
        sys.exit(1)


def submit(signed_file_path: str, socket_path: str, network: str, cli_path: str, logger=None) -> bool:
    """Submit the transaction to the blockchain.
    """
    func = [
        cli_path,
        'conway',
        'transaction',
        'submit',
        '--socket-path', socket_path,
        '--tx-file',
        signed_file_path
    ]
    func += network.split(" ")

    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    if logger is not None:
        logger.debug(f"Submit Output: {output}")
        logger.debug(f"Submit Errors: {errors}")
    if "Connection refused" in errors.decode():
        sys.exit(1)
    if "Command failed" in errors.decode():
        return False
    if "Transaction successfully submitted" in output.decode():
        return True
    # if it didnt fail nicely or didnt submit then fail it
    return False
