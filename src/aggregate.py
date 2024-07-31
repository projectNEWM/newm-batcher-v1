import os

from loguru._logger import Logger

from src.address import pkh_from_address
from src.cli import does_tx_exists_in_mempool, sign, submit, txid
from src.datums import (data_validity, oracle_validity, sale_validity,
                        vault_validity)
from src.db_manager import DbManager
from src.endpoint import Endpoint
from src.utility import file_exists, parent_directory_path, sha3_256
from src.utxo_manager import UTxOManager


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

        batcher_infos = db.batcher.read_all()

        # batcher pkh for signing will come from vault now
        batcher_pkh = pkh_from_address(config['batcher_address'])
        vault_info = db.vault.read(batcher_pkh)
        if vault_info is None:
            logger.critical("Vault is not set up for batcher")
            return
        if vault_validity(vault_info['datum']) is False:
            logger.critical("Vault has failed the validity test")
            return

        oracle_info = db.oracle.read()
        if oracle_info is None:
            logger.critical("Oracle is not set up for batcher")
            return
        if oracle_validity(oracle_info['datum']) is False:
            logger.critical("Oracle has failed the validity test")
            return

        data_info = db.data.read()
        if data_info is None:
            logger.critical("Data is not set up for batcher")
            return
        if data_validity(data_info['datum']) is False:
            logger.critical("Data has failed the validity test")
            return

        batcher_info, profit_success_flag = Endpoint.profit(batcher_infos, config)
        # no utxos or no batcher token
        if batcher_info is None:
            logger.critical("Batcher is returning None from profit endpoint")
            return

        if profit_success_flag is True:
            # sign and submit tx here
            sign(out_file_path, signed_profit_tx, config['network'], batcher_skey_path)
            if submit(signed_profit_tx, config["socket_path"], config["network"], logger):
                # if submit was successful then delete what was spent and add in the new outputs
                #
                # TODO
                #
                # Is deleting here what we want to do?
                for batcher in batcher_infos:
                    tag = sha3_256(batcher['txid'])
                    if db.batcher.delete(tag):
                        logger.success(f"Spent Batcher Input @ {tag}")
                tag = sha3_256(batcher_info['txid'])
                db.batcher.create(tag, batcher_info['txid'], batcher_info['value'])
                logger.success(f"Batcher Output @ {batcher_info['txid']}")
            else:
                logger.warning("Batcher Profit Transaction Failed")
                # attempt to get the db batcher utxo then
                batcher_info = db.batcher.read(config("batcher_policy"))
                if batcher_info is None:
                    logger.critical("Batcher UTxO can not be found")
                    return
        # create the UTxOManger
        utxo = UTxOManager(batcher_info, data_info, oracle_info, vault_info)

        # handle the sales now
        for sale_tkn in sorted_queue:
            sale_info = db.sale.read(sale_tkn)
            if sale_validity(sale_info['datum']) is False:
                logger.warning(f"Sale: {sale_tkn} has failed the validity test")
                # skip this sale as something is wrong
                continue

            # set the sale now that we know it
            utxo.set_sale(sale_info)

            orders = sorted_queue[sale_tkn]
            if len(orders) == 0:
                continue

            logger.debug(f"Sale: {sale_tkn}")
            for order_data in orders:
                order_hash = order_data[0]
                queue_info = db.queue.read(order_hash)

                # check if the order is in the db
                if queue_info is None:
                    logger.warning(f"Order: {order_hash} Not Found")
                    # skip this order its not in the db
                    continue

                # check if the tag has been seen before
                if db.seen.read(queue_info["tag"]) is True:
                    logger.warning(f"Order: {order_hash} Has Been Seen")
                    # skip this order as its already been seen
                    continue

                logger.debug(f"Queue: {order_hash}")

                # set the queue now that we know it
                utxo.set_queue(queue_info)

                # build the purchase tx
                utxo, purchase_success_flag = Endpoint.purchase(utxo, config, None)
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
                utxo, refund_success_flag = Endpoint.refund(utxo, config, None)
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
                        #
                        # TODO
                        #
                        # Seen may need to be removed
                        # db.seen.create(order_hash)
                        # db.seen.create(tag)
                    else:
                        logger.warning(f"Order: {order_hash} Purchased: Failed")

                # submit tx
                if refund_success_flag is True:
                    refund_result = submit(signed_refund_tx, config['socket_path'], config['network'])
                    tag = sha3_256(txid(signed_refund_tx))
                    if refund_result is True:
                        logger.success(f"Order: {tag} Refund: {refund_result}")
                        # db.seen.create(tag)
                    else:
                        logger.warning(f"Order: {tag} Refund: Failed")
        return
