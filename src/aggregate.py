import copy
import os

from loguru._logger import Logger

from src.cli import does_tx_exists_in_mempool, sign, submit, txid
from src.datums import sale_validity
from src.db_manager import DbManager
from src.endpoint import Endpoint
from src.utility import file_exists, parent_directory_path, sha3_256


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
        batcher_skey_path = os.path.join(parent_dir, "keys/batcher.skey")
        collat_skey_path = os.path.join(parent_dir, "keys/collat.skey")

        if file_exists(batcher_skey_path) is False:
            logger.critical("Batcher Secret Key Is Missing!")
            return

        batcher_infos = db.read_all_batcher()

        batcher, profit_success_flag = Endpoint.profit(batcher_infos, config)
        # no utxos or no batcher token
        if batcher is None:
            logger.debug("Batcher is returning None from profit endpoint")
            return

        if profit_success_flag is True:
            # sign and submit tx here
            sign(out_file_path, signed_profit_tx, config['network'], batcher_skey_path)
            if submit(signed_profit_tx, config["socket_path"], config["network"], logger):
                # if submit was successful then delete what was spent and add in the new outputs
                for batcher_info in batcher_infos:
                    tag = sha3_256(batcher_info['txid'])
                    if db.delete_batcher(tag):
                        logger.success(f"Spent Batcher Input @ {tag}")
                tag = sha3_256(batcher['txid'])
                db.create_batcher(tag, batcher['txid'], batcher['value'])
                logger.success(f"Batcher Output @ {batcher['txid']}")
            else:
                logger.warning("Batcher Profit Transaction Failed")
                # attempt to get the db batcher utxo then
                batcher = db.read_batcher(config("batcher_policy"))
                if batcher is None:
                    logger.warning("Batcher UTxO can not be found")
                    return

        # handle the sales now
        for sale_tkn in sorted_queue:
            sale = db.read_sale(sale_tkn)
            if sale_validity(sale['datum']) is False:
                logger.warning(f"Sale: {sale_tkn} has failed the validity test")
                # skip this sale as something is wrong
                continue

            orders = sorted_queue[sale_tkn]
            if len(orders) == 0:
                continue

            logger.debug(f"Sale: {sale_tkn}")
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

                logger.debug(f"Queue: {order_hash}")
                # build the purchase tx
                new_sale, new_order, new_batcher, purchase_success_flag = Endpoint.purchase(copy.deepcopy(sale), copy.deepcopy(order), copy.deepcopy(batcher), config)
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
                    sign(out_file_path, signed_purchase_tx, config['network'], batcher_skey_path, collat_skey_path)

                #
                # The order may just be in the refund state
                #
                # assume its good to go and lets chain the refund
                new_new_sale, new_new_order, new_new_batcher, refund_success_flag = Endpoint.refund(copy.deepcopy(new_sale), copy.deepcopy(new_order), copy.deepcopy(new_batcher), config)
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
                    sign(out_file_path, signed_refund_tx, config['network'], batcher_skey_path, collat_skey_path)

                # submit tx
                if purchase_success_flag is True:
                    purchase_result = submit(signed_purchase_tx, config['socket_path'], config['network'])
                    if purchase_result is True:
                        logger.success(f"Order: {order_hash} Purchased: {purchase_result}")
                        tag = sha3_256(txid(signed_purchase_tx))
                        db.create_seen(order_hash)
                        db.create_seen(tag)
                        sale = copy.deepcopy(new_sale)
                        batcher = copy.deepcopy(new_batcher)
                    else:
                        logger.warning(f"Order: {order_hash} Purchased: Failed")

                # submit tx
                if refund_success_flag is True:
                    refund_result = submit(signed_refund_tx, config['socket_path'], config['network'])
                    tag = sha3_256(txid(signed_refund_tx))
                    if refund_result is True:
                        logger.success(f"Order: {tag} Refund: {refund_result}")
                        db.create_seen(tag)
                        sale = copy.deepcopy(new_new_sale)
                        batcher = copy.deepcopy(new_new_batcher)
                    else:
                        logger.warning(f"Order: {tag} Refund: Failed")
        return
