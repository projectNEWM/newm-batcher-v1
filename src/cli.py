import datetime
import json
import subprocess
import sys


def query_slot_number(socket: str, unix_time: int, network: str, delta: int = 0) -> int:
    timestamp = datetime.datetime.fromtimestamp((unix_time / 1000) + delta, tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    func = [
        'cardano-cli',
        'query',
        'slot-number',
        '--socket-path',
        socket
    ]
    func += network.split(" ")
    func += [timestamp]
    # this saves to out file
    p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()
    # exit application if node is not live
    if "Connection refused" in errors.decode():
        sys.exit(1)
    # decode output into int
    return int(output.decode())


def query_protocol_parameters(socket: str, file_path: str, network: str) -> None:
    """Query the protocol parameters for a given network.

    Args:
        socket (str): The node socket path
        file_path (str): The output file path
        network (str): The network flag
    """
    func = [
        'cardano-cli',
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


def query_tx_mempool(socket: str, tx_id: str, file_path: str, network: str) -> None:
    """
    Query the tx mempool and check if a specific transaction exists inside of it.

    Args:
        socket (str): The node socket path
        tx_id (str): The transaction id
        file_path (str): The output file path
        network (str): The network flag
    """
    func = [
        'cardano-cli',
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


def does_tx_exists_in_mempool(socket: str, tx_id: str, file_path: str, network: str) -> bool:
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
    query_tx_mempool(socket, tx_id, file_path, network)
    # get the block data
    with open(file_path, "r") as read_content:
        data = json.load(read_content)
    return data['exists']


def query_tip(socket: str, file_path: str, network: str) -> None:
    """
    Query the tip of the blockchain then save to a file.

    Args:
        socket (str): The socket path to the node
        file_path (str): The output file path
        network (str): The network flag
    """
    func = [
        'cardano-cli',
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


def get_latest_block_number(socket: str, file_path: str, network: str) -> int:
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
    query_tip(socket, file_path, network)

    # get the block data
    with open(file_path, "r") as read_content:
        data = json.load(read_content)

    return int(data['block'])


def txid(file_path: str) -> str:
    """
    Get the tx id of a signed transactions.

    Args:
        file_path (str): The transaction file path.

    Returns:
        str: The transaction id
    """
    func = [
        'cardano-cli',
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


def sign(draft_file_path: str, signed_file_path: str, network: str, skey_path: str, collat_path: str = None) -> None:
    """Sign a transaction with a list of payment keys.
    """
    func = [
        'cardano-cli',
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


def submit(signed_file_path: str, socket_path: str, network: str, logger=None) -> bool:
    """Submit the transaction to the blockchain.
    """
    func = [
        'cardano-cli',
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
        logger.debug(output)
        logger.debug(errors)
    if "Connection refused" in errors.decode():
        sys.exit(1)
    if "Command failed" in errors.decode():
        return False
    if "Transaction successfully submitted" in output.decode():
        return True
    # if it didnt fail nicely or didnt submit then fail it
    return False
