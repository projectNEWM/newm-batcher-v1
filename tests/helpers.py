import subprocess


def is_node_live(socket):
    try:
        func = [
            'cardano-cli',
            'ping',
            '--count', '1',
            '--unixsock', socket,
            '--json',
            '--quiet',
        ]
        result = subprocess.run(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False


if __name__ == "__main__":
    socket_path = "/home/logic/Documents/Work/LogicalMechanism/testnets/node-preprod/db-testnet/node.socket"
    print(is_node_live(socket_path))
