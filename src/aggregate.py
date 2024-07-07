import os

from loguru._logger import Logger

from src.cli import does_tx_exists_in_mempool, sign, submit, txid
from src.datums import sale_validity
from src.db_manager import DbManager
from src.endpoint import Endpoint
from src.utility import parent_directory_path, sha3_256


class Aggregate:

    @staticmethod
    def orders(db: DbManager, sorted_queue: dict, config: dict, logger: Logger) -> None:
        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        out_file_path = os.path.join(parent_dir, "tmp/tx.draft")
        mempool_file_path = os.path.join(parent_dir, "tmp/mempool.json")
        signed_purchase_tx = os.path.join(parent_dir, "tmp/queue-purchase-tx.signed")
        signed_refund_tx = os.path.join(parent_dir, "tmp/queue-refund-tx.signed")
        signed_profit_tx = os.path.join(parent_dir, "tmp/batcher-profit-tx.signed")
        batcher_skey_path = os.path.join(parent_dir, "key/batcher.skey")

        batcher_infos = db.read_all_batcher()
        batcher, profit_success_flag = Endpoint.profit(batcher_infos, config)
        # no utxos or no batcher token
        if batcher is None:
            return

        if profit_success_flag is True:
            # sign and submit tx here
            sign(out_file_path, signed_profit_tx, config['network'], batcher_skey_path)
            if submit(signed_profit_tx, config["socket_path"], config["network"]):
                logger.success(f"Batcher Profit: {txid(signed_profit_tx)}")
            else:
                logger.warning("Batcher Profit Transaction Failed")
                # attempt to get the db batcher utxo then
                batcher = db.read_batcher(config("batcher_policy"))
                if batcher is None:
                    return

        # handle the sales now
        for sale_tkn in sorted_queue:
            sale = db.read_sale(sale_tkn)
            if sale_validity(sale['datum']) is False:
                # skip this sale as something is wrong
                continue

            orders = sorted_queue[sale_tkn]
            for order_data in orders:
                order_hash = order_data[0]
                order = db.read_queue(order_hash)

                # check if the order is in the db
                if order is None:
                    logger.warning(f"Order: {order_hash} Not Found")
                    # skip this order its not in the db
                    continue

                # check if the tag has been seen before
                if db.read_seen(order["tag"]) is True:
                    logger.warning(f"Order: {order_hash} Has Been Seen")
                    # skip this order as its already been seen
                    continue

                # build the purchase tx
                new_sale, new_order, new_batcher, purchase_success_flag = Endpoint.purchase(sale, order, batcher, config)
                # if the flag is false then some valdation failed or build failed
                if purchase_success_flag is False:
                    logger.warning(f"User Must Remove Order: {order_hash} Or May Be In Refund State")

                # if the purchase was successful then sign it and update the info
                if purchase_success_flag is True:
                    # lets check if this tx was already submitted to the mempool
                    intermediate_txid = txid(out_file_path)
                    if does_tx_exists_in_mempool(config["socket_path"], intermediate_txid, mempool_file_path, config["network"]):
                        logger.warning(f"Transaction: {intermediate_txid} Is In Mempool")
                        # skip the sign and submit since it was already submitted
                        continue
                    # sign tx
                    sign(out_file_path, signed_purchase_tx, config['network'], batcher_skey_path)

                    # if good then attempt to tx chain
                    sale = new_sale
                    order = new_order
                    batcher = new_batcher

                #
                # The order may just be in the refund state
                #

                # assume its good to go and lets chain the refund
                new_sale, new_order, new_batcher, refund_success_flag = Endpoint.refund(sale, order, batcher, config)
                # if this fails then do not move forward
                if refund_success_flag is False:
                    logger.warning(f"Missing Incentive: User Must Remove Order: {order_hash}")
                    # skip the sign and submit as something didn't validate from the order
                    continue

                # if the refund build was success then sign and submit
                if refund_success_flag is True:
                    # refund was built correctly
                    # lets check if this tx was already submitted then
                    intermediate_txid = txid(out_file_path)
                    if does_tx_exists_in_mempool(config["socket_path"], intermediate_txid, mempool_file_path, config["network"]):
                        logger.warning(f"Transaction: {intermediate_txid} Is In Mempool")
                        # skip the sign and submit since it was already submitted
                        continue
                    # sign tx
                    sign(out_file_path, signed_refund_tx, config['network'], batcher_skey_path)

                    # if good then attempt to tx chain
                    sale = new_sale
                    batcher = new_batcher

                # submit tx
                purchase_result, _ = submit(signed_purchase_tx, config['socket_path'], config['network'])
                if purchase_result is True:
                    logger.success(f"Order: {order_hash} Purchased: {purchase_result}")
                    tag = sha3_256(txid(signed_purchase_tx))
                    db.create_seen(order_hash)
                    db.create_seen(tag)

                # submit tx
                refund_result, _ = submit(signed_refund_tx, config['socket_path'], config['network'])
                if refund_result is True:
                    tag = sha3_256(txid(signed_refund_tx))
                    logger.success(f"Order: {tag} Refund: {refund_result}")
                    db.create_seen(tag)
        return