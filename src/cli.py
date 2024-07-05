import json
import subprocess
import sys


def query_tx_mempool(socket, tx_id, file_path, network):
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

    if "cardano-cli" in errors.decode():
        sys.exit(1)


def does_tx_exists_in_mempool(socket, tx_id, file_path, network):
    """
    Check if a tx exists in the nodes local mempool.
    """
    # check the mempool
    query_tx_mempool(socket, tx_id, file_path, network)
    # get the block data
    with open(file_path, "r") as read_content:
        data = json.load(read_content)
    return data['exists']
