import argparse
import json
import sys

from src import yaml_file
from src.cli import get_latest_block_number
from src.datums import queue_validity, sale_validity
from src.db_manager import DbManager
from src.sorting import Sorting

config = yaml_file.read("config.yaml")


def status(db: DbManager):
    latest_block_number = get_latest_block_number(config['socket_path'], 'tmp/tip.json', config['network'])
    db_status = db.read_status()

    tip_difference = latest_block_number - int(db_status['block_number'])
    if tip_difference - config['delay_depth'] == 0:
        print("Batcher Is Synced")
    else:
        print(f"{tip_difference} Blocks Til Synced")
    print(f"Current Status: {db_status}")


def batcher_utxos(db: DbManager):
    print(f"\n{config['batcher_address']}")
    utxos = db.read_all_batcher()
    if len(utxos) == 0:
        print("No Batcher UTxOs")
    for utxo in utxos:
        print(f"\n{utxo['txid']}\n")
        print(f"{utxo['value']}")


def sale_utxos(db: DbManager):
    tkns = db.read_all_sale_tkns()
    for tkn in tkns:
        sale = db.read_sale(tkn)
        queues = db.read_all_queue(tkn)
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
    sale = db.read_sale(tkn)
    if sale is None:
        print("Sale Has Been Removed")
    else:
        print(f"Sale TxId: {sale['txid']}")
        print(json.dumps(sale['datum'], indent=4))
        print(f"{sale['value']}")
        queues = db.read_all_queue(tkn)
        n_queue_entries = len(queues)
        print(f"\nThere are {n_queue_entries} Queue Entries For {tkn}:")
        for queue in queues:
            data = queue[1]
            print(f"\n{data['txid']} is valid: {queue_validity(data['datum'])}")
            print(f"{data['value']}")


def query_order(db: DbManager, tag: str):
    entry = db.read_queue(tag)
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


def main():
    parser = argparse.ArgumentParser(description='NEWM-Batcher Database Analysis Tool')
    parser.add_argument('-s', '--status', action='store_true', help='return the current sync status')
    parser.add_argument('--batcher', action='store_true', help='return the batcher UTxOs')
    parser.add_argument('--sales', action='store_true', help='return the sale UTxOs and queue entries')
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
