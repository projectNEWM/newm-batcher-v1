import os

from loguru._logger import Logger

from src.address import pkh_from_address
from src.cli import (does_tx_exists_in_mempool, does_utxo_exist, sign, submit,
                     txid)
from src.datums import (data_validity, oracle_validity, sale_validity,
                        vault_validity)
from src.db_manager import DbManager
from src.endpoint import Endpoint
from src.utility import current_time, file_exists, parent_directory_path
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

        # does the batcher utxo actually exist still if the profit wasnt successful
        for info in batcher_infos:
            if does_utxo_exist(config["socket_path"], info['txid'], config["network"], config["cli_path"]) is False:
                logger.warning(f"Batcher: {info['txid']} does not exist on chain")
                # then its not in the utxo set right now
                return

        # batcher pkh for signing will come from vault now
        batcher_pkh = pkh_from_address(config['batcher_address'])

        # vault
        vault_infos = db.vault.read_all(batcher_pkh)
        if vault_infos is None:
            logger.critical("Vaults is not set up for batcher")
            return
        # find one
        for info in vault_infos:
            use_this_vault_flag = True
            # does is the vault datum valid?
            if vault_validity(info['datum']) is False:
                logger.critical("Vault has failed the validity test")
                use_this_vault_flag = False
                continue
            # does the vault utxo actually exist still?
            if does_utxo_exist(config["socket_path"], info['txid'], config["network"], config["cli_path"]) is False:
                logger.warning(f"Vault: {info['txid']} does not exist on chain")
                use_this_vault_flag = False
                continue
            # if good to go then set the vault info and break
            if use_this_vault_flag is True:
                vault_info = info
                break
        if use_this_vault_flag is False:
            # then all the vaults
            logger.critical("All Vaults do not exist on chain")
            return

        # oracle
        oracle_info = db.oracle.read()
        if oracle_info is None:
            logger.critical("Oracle is not set up for batcher")
            return
        if oracle_validity(oracle_info['datum']) is False:
            logger.critical("Oracle has failed the validity test")
            return
        # does the oracle utxo actually exist still?
        if does_utxo_exist(config["socket_path"], oracle_info['txid'], config["network"], config["cli_path"]) is False:
            logger.warning(f"Oracle: {oracle_info['txid']} does not exist on chain")
            # then its not in the utxo set right now
            return

        # data
        data_info = db.data.read()
        if data_info is None:
            logger.critical("Data is not set up for batcher")
            return
        if data_validity(data_info['datum']) is False:
            logger.critical("Data has failed the validity test")
            return
        # does the data utxo actually exist still?
        if does_utxo_exist(config["socket_path"], data_info['txid'], config["network"], config["cli_path"]) is False:
            logger.warning(f"Data: {data_info['txid']} does not exist on chain")
            # then its not in the utxo set right now
            return

        # batcher info is returned from the profit endpoint
        batcher_info, profit_success_flag = Endpoint.profit(batcher_infos, config)

        # no utxos or no batcher token
        if batcher_info is None:
            logger.critical("Batcher UTxO can not be found")
            return

        if profit_success_flag is True:
            # sign and submit tx here
            sign(out_file_path, signed_profit_tx, config['network'], batcher_skey_path, config["cli_path"])
            if submit(signed_profit_tx, config["socket_path"], config["network"], config["cli_path"], logger):
                # if submit was successful then batcher goes into the depth delay cooldown
                logger.success(f"Auto Profit Batcher Output @ {batcher_info['txid']}")
                #
                # TODO Do we have to return here?
                #
                return
            else:
                logger.warning("Batcher Profit Transaction Failed")
                # attempt to get the db batcher utxo then
                batcher_info = db.batcher.read(config["batcher_policy"])
                if batcher_info is None:
                    logger.critical("Batcher UTxO can not be found")
                    return

        # reference info
        reference_info = db.reference.read()

        # create the UTxOManger
        utxo = UTxOManager(batcher_info, data_info, oracle_info, vault_info, reference_info)

        # delete all expired seen entries
        db.seen.delete(current_time())

        # handle the sales now
        for sale_tkn in sorted_queue:
            sale_info = db.sale.read(sale_tkn)
            if sale_validity(sale_info['datum']) is False:
                logger.warning(f"Sale: {sale_tkn} has failed the validity test")
                # skip this sale as something is wrong
                continue

            # does the sale utxo actually exist still?
            if does_utxo_exist(config["socket_path"], sale_info['txid'], config["network"], config["cli_path"]) is False:
                logger.warning(f"Sale: {sale_info['txid']} does not exist on chain")
                # then its not in the utxo set right now
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

                # does the queue utxo actually exist still?
                if does_utxo_exist(config["socket_path"], queue_info['txid'], config["network"], config["cli_path"]) is False:
                    logger.warning(f"Queue: {queue_info['txid']} does not exist on chain")
                    # then its not in the utxo set right now
                    continue

                if db.seen.exists(queue_info['txid']) is True:
                    logger.warning(f"Queue: {queue_info['txid']} may still be in the mempool")
                    # then its not in the utxo set right now
                    continue

                logger.debug(f"Queue: {queue_info['txid']}")

                # set the queue now that we know it
                utxo.set_queue(queue_info)

                # build the purchase tx
                start_time = utxo.oracle.datum['fields'][0]['fields'][0]['map'][1]['v']['int']
                end_time = utxo.oracle.datum['fields'][0]['fields'][0]['map'][2]['v']['int']

                purchase_input = utxo.queue.txid
                utxo, purchase_success_flag = Endpoint.purchase(utxo, config, logger=logger)
                # if the flag is false then some valdation failed or build failed
                if purchase_success_flag is False:
                    logger.warning(f"Order: {purchase_input}: Remove Only Or Refund")

                # if the purchase was successful then sign it and update the info
                if purchase_success_flag is True:
                    # lets check if this tx was already submitted to the mempool
                    intermediate_txid = txid(out_file_path, config["cli_path"])
                    if does_tx_exists_in_mempool(config["socket_path"], intermediate_txid, mempool_file_path, config["network"], config["cli_path"]):
                        logger.warning(f"Transaction: {intermediate_txid} Is In Mempool")
                        # skip the sign and submit since it was already submitted
                        continue
                    # sign tx
                    sign(out_file_path, signed_purchase_tx, config['network'], batcher_skey_path, config["cli_path"], collat_skey_path)

                #
                # The order may just be in the refund state
                #
                # assume its good to go and lets chain the refund
                refund_input = utxo.queue.txid
                utxo, refund_success_flag = Endpoint.refund(utxo, config, logger=logger)
                # if this fails then do not move forward
                if refund_success_flag is False:
                    logger.warning(f"Order: {refund_input}: Remove Only")
                    # skip the sign and submit as something didn't validate from the order
                    continue

                # if the refund build was success then sign and submit
                if refund_success_flag is True:
                    # refund was built correctly
                    # lets check if this tx was already submitted then
                    intermediate_txid = txid(out_file_path, config["cli_path"])
                    if does_tx_exists_in_mempool(config["socket_path"], intermediate_txid, mempool_file_path, config["network"], config["cli_path"]):
                        logger.warning(f"Transaction: {intermediate_txid} Is In Mempool")
                        # skip the sign and submit since it was already submitted
                        continue
                    # sign tx
                    sign(out_file_path, signed_refund_tx, config['network'], batcher_skey_path, config["cli_path"], collat_skey_path)

                # submit tx
                if purchase_success_flag is True:
                    purchase_result = submit(signed_purchase_tx, config['socket_path'], config['network'], config["cli_path"], logger)
                    logger.success(f"Order: {purchase_input} Purchased: {purchase_result}")
                    if purchase_result is True:
                        # saw something go into the mempool with this validity window
                        db.seen.create(purchase_input, start_time, end_time)

                # submit tx
                if refund_success_flag is True:
                    refund_result = submit(signed_refund_tx, config['socket_path'], config['network'], config["cli_path"], logger)
                    logger.success(f"Order: {refund_input} Refund: {refund_result}")
                    if refund_result is True:
                        # saw something go into the mempool with this validity window
                        db.seen.create(refund_input, start_time, end_time)
        return
