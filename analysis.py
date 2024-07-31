import argparse
import json
import sys
import time

from src import yaml_file
from src.address import pkh_from_address
from src.cli import get_latest_block_number
from src.datums import queue_validity, sale_validity
from src.db_manager import DbManager
from src.sorting import Sorting

config = yaml_file.read("config.yaml")


def status(db: DbManager):
    latest_block_number = get_latest_block_number(config['socket_path'], 'tmp/tip.json', config['network'])
    db_status = db.status.read()

    tip_difference = latest_block_number - int(db_status['block_number'])
    if tip_difference - config['delay_depth'] == 0:
        print("Batcher Is Synced")
    else:
        print(f"{tip_difference} Blocks Til Synced")
    print(f"Current Status: {db_status}")


def batcher_utxos(db: DbManager):
    print(f"\n{config['batcher_address']}")
    utxos = db.batcher.read_all()
    if len(utxos) == 0:
        print("No Batcher UTxOs")
    for utxo in utxos:
        print(f"\n{utxo['txid']}\n")
        print(f"{utxo['value']}")


def sale_utxos(db: DbManager):
    tkns = db.sale.read_all()
    for tkn in tkns:
        sale = db.sale.read(tkn)
        queues = db.queue.read_all(tkn)
        print("\nSale:")
        print(f"{tkn} is valid: {sale_validity(sale['datum'])}")
        print(f"{sale['txid']}")
        print(json.dumps(sale['datum'], indent=4))
        print(f"{sale['value']}")
        n_queue_entries = len(queues)
        if n_queue_entries > 0:
            print(f"\nThere are {n_queue_entries} Queue Entries For {tkn}:")
            for queue in queues:
                data = queue[1]
                print(f"\n{data['txid']} is valid: {queue_validity(data['datum'])}")
                print(f"{data['value']}")


def query_sale(db: DbManager, tkn: str):
    sale = db.sale.read(tkn)
    if sale is None:
        print("Sale Has Been Removed")
    else:
        print(f"Sale TxId: {sale['txid']}")
        print(json.dumps(sale['datum'], indent=4))
        print(f"{sale['value']}")
        queues = db.queue.read_all(tkn)
        n_queue_entries = len(queues)
        print(f"\nThere are {n_queue_entries} Queue Entries For {tkn}:")
        for queue in queues:
            data = queue[1]
            print(f"\n{data['txid']} is valid: {queue_validity(data['datum'])}")
            print(f"{data['value']}")


def query_order(db: DbManager, tag: str):
    entry = db.queue.read(tag)
    if entry is None:
        print("Queue Entry Has Been Removed")
    else:
        print(f"\n{entry['txid']} is valid: {queue_validity(entry['datum'])}")
        print(json.dumps(entry['datum'], indent=4))
        print(f"{entry['value']}")


def sorted_queue(db: DbManager):
    sorted_queue = Sorting.fifo(db)
    print(f"There are {len(sorted_queue)} Live Sales")
    for order in sorted_queue:
        n_orders = len(sorted_queue[order])
        if n_orders > 0:
            print(f"\nSale Order: {order} has {n_orders} Queue Entries")
            print("----------------------------------------------------------")
            for entry in sorted_queue[order]:
                print(f"Queue Entry: {entry[0]}")


def oracle_utxo(db: DbManager):
    record = db.oracle.read()
    try:
        print(f"Oracle TxId: {record['txid']}")
        print(json.dumps(record['datum'], indent=4))
        time_left = int(record['datum']['fields'][0]['fields'][0]['map'][2]['v']['int'] / 1000) - int(time.time())
        current_price = record['datum']['fields'][0]['fields'][0]['map'][0]['v']['int'] / 1000000
        print(f"{time_left} seconds remaining which is about {time_left / 60} minutes")
        print(f"Current Price: {current_price} USD")
    except TypeError:
        print("Oracle Never Updated")


def data_utxo(db: DbManager):
    record = db.data.read()
    try:
        print(f"Data TxId: {record['txid']}")
        print(json.dumps(record['datum'], indent=4))
    except (TypeError, KeyError):
        print("Oracle Never Updated")


def vault_utxo(db: DbManager):
    # batcher pkh for signing
    batcher_pkh = pkh_from_address(config['batcher_address'])
    record = db.vault.read(batcher_pkh)
    try:
        print(f"Vault TxId: {record['txid']}")
        print(json.dumps(record['datum'], indent=4))
        print(f"{record['value']}")
    except (TypeError, KeyError):
        print("Vault Does Not Exist")


def main():
    parser = argparse.ArgumentParser(description='NEWM-Batcher Database Analysis Tool')
    parser.add_argument('-s', '--status', action='store_true', help='return the current sync status')
    parser.add_argument('--batcher', action='store_true', help='return the batcher UTxOs')
    parser.add_argument('--oracle', action='store_true', help='return the oracle UTxO')
    parser.add_argument('--data', action='store_true', help='return the data UTxO')
    parser.add_argument('--sales', action='store_true', help='return the sale UTxOs and queue entries')
    parser.add_argument('--vault', action='store_true', help='return the vault UTxOs')
    parser.add_argument('--query-sale', type=str, help='return the queue entries for a sale')
    parser.add_argument('--query-order', type=str, help='return the queue info for a queue entry')
    parser.add_argument('--sorted-queue', action='store_true', help='return the sorted sale UTxOs and queue entries')

    args = parser.parse_args()

    # Show help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    db_manager = DbManager()

    if args.status:
        status(db_manager)

    if args.batcher:
        batcher_utxos(db_manager)

    if args.oracle:
        oracle_utxo(db_manager)

    if args.data:
        data_utxo(db_manager)

    if args.vault:
        vault_utxo(db_manager)

    if args.sales:
        sale_utxos(db_manager)

    if args.query_sale:
        query_sale(db_manager, args.query_sale)

    if args.query_order:
        query_order(db_manager, args.query_order)

    if args.sorted_queue:
        sorted_queue(db_manager)


if __name__ == '__main__':
    main()
