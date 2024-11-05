import subprocess


def is_node_live(socket, magic=1, cli_path='cardano-cli'):
    try:
        func = [
            cli_path,
            'ping',
            '--count', '1',
            '--unixsock', socket,
            '--magic', str(magic),
            '--json',
            '--quiet',
        ]
        result = subprocess.run(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False
