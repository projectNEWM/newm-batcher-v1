from loguru._logger import Logger

from src.db_manager import DbManager
from src.parse import asset_list_to_value
from src.utility import sha3_256


class IOManager:
    ###########################################################################
    # Inputs
    ###########################################################################
    @staticmethod
    def spent_input(db: DbManager, data: dict, logger: Logger) -> None:
        # the tx hash of this transaction
        input_utxo = data['tx_input']['tx_id'] + '#' + str(data['tx_input']['index'])

        # sha3_256 hash of the input utxo
        utxo_base_64 = sha3_256(input_utxo)
        
        # attempt to delete from the dbs 
        if db.batcher.delete(utxo_base_64):
            logger.success(f"Spent Batcher Input @ {input_utxo} @ Timestamp {data['context']['timestamp']}")

        if db.sale.delete(input_utxo):
            logger.success(f"Spent Sale Input @ {input_utxo} @ Timestamp {data['context']['timestamp']}")

        if db.queue.delete(utxo_base_64):
            logger.success(f"Spent Queue Input: {input_utxo} @ Timestamp {data['context']['timestamp']}")

        if db.vault.delete(utxo_base_64):
            logger.success(f"Spent Vault Input: {input_utxo} @ Timestamp {data['context']['timestamp']}")

    ###########################################################################
    # Outputs
    ###########################################################################

    @staticmethod
    def batcher_output(db: DbManager, config: dict, data: dict, logger: Logger) -> None:
        # the context of this transaction
        context = data['context']

        output_utxo = context['tx_hash'] + '#' + str(context['output_idx'])
        utxo_base_64 = sha3_256(output_utxo)

        if data['tx_output']['address'] == config['batcher_address']:
            value_obj = asset_list_to_value(data['tx_output']['assets'])
            value_obj.add_lovelace(data['tx_output']['amount'])

            db.batcher.create(utxo_base_64, output_utxo, value_obj)
            logger.success(f"Batcher Output @ {output_utxo} @ Timestamp: {context['timestamp']}")

    @staticmethod
    def sale_output(db: DbManager, config: dict, data: dict, logger: Logger) -> None:
        # the context of this transaction
        context = data['context']

        # the utxo
        output_utxo = context['tx_hash'] + '#' + str(context['output_idx'])

        if data['tx_output']['address'] == config['sale_address']:
            # get the datum
            sale_datum = data['tx_output']['inline_datum']['plutus_data'] if data['tx_output']['inline_datum'] is not None else {}

            value_obj = asset_list_to_value(data['tx_output']['assets'])
            value_obj.add_lovelace(data['tx_output']['amount'])

            # only create a sale if the sale has the pointer token
            if value_obj.exists(config['pointer_policy']):
                # get the token name from the pointer policy
                tkn = value_obj.get_token(config['pointer_policy'])
                db.sale.create(tkn, output_utxo, sale_datum, value_obj)
                logger.success(f"Sale Output @ {output_utxo} @ Timestamp: {context['timestamp']}")

    @staticmethod
    def queue_output(db: DbManager, config: dict, data: dict, logger: Logger) -> None:
        context = data['context']
        # timestamp for ordering, equal timestamps use the tx_idx to order
        timestamp = context['timestamp']
        tx_idx = context['tx_idx']

        output_utxo = context['tx_hash'] + '#' + str(context['output_idx'])
        utxo_base_64 = sha3_256(output_utxo)

        # check if its the queue contract
        if data['tx_output']['address'] == config['queue_address']:
            # get the queue datum
            queue_datum = data['tx_output']['inline_datum']['plutus_data'] if data['tx_output']['inline_datum'] is not None else {}

            # get the pointer token
            pointer_token = queue_datum['fields'][3]['bytes']

            value_obj = asset_list_to_value(data['tx_output']['assets'])
            value_obj.add_lovelace(data['tx_output']['amount'])

            db.queue.create(utxo_base_64, output_utxo, pointer_token, queue_datum, value_obj, timestamp, tx_idx)
            logger.success(f"Queue Output @ {output_utxo} @ Timestamp: {timestamp}")

    @staticmethod
    def vault_output(db: DbManager, config: dict, data: dict, logger: Logger) -> None:
        context = data['context']
        # timestamp for ordering, equal timestamps use the tx_idx to order
        timestamp = context['timestamp']

        output_utxo = context['tx_hash'] + '#' + str(context['output_idx'])
        utxo_base_64 = sha3_256(output_utxo)

        # check if its the queue contract
        if data['tx_output']['address'] == config['vault_address']:
            # get the queue datum
            vault_datum = data['tx_output']['inline_datum']['plutus_data'] if data['tx_output']['inline_datum'] is not None else {}

            pkh = vault_datum['fields'][0]['bytes']

            value_obj = asset_list_to_value(data['tx_output']['assets'])
            value_obj.add_lovelace(data['tx_output']['amount'])

            db.vault.create(utxo_base_64, output_utxo, pkh, vault_datum, value_obj)
            logger.success(f"Vault Output @ {output_utxo} @ Timestamp: {timestamp}")

    @staticmethod
    def oracle_output(db: DbManager, config: dict, data: dict, logger: Logger) -> None:
        context = data['context']
        # timestamp for ordering, equal timestamps use the tx_idx to order
        timestamp = context['timestamp']

        output_utxo = context['tx_hash'] + '#' + str(context['output_idx'])
        # check if its the queue contract
        if data['tx_output']['address'] == config['oracle_address']:
            oracle_datum = data['tx_output']['inline_datum']['plutus_data'] if data['tx_output']['inline_datum'] is not None else {}

            value_obj = asset_list_to_value(data['tx_output']['assets'])
            value_obj.add_lovelace(data['tx_output']['amount'])

            if value_obj.get_quantity(config['oracle_policy'], config['oracle_asset']) == 1:
                db.oracle.update(output_utxo, oracle_datum)
                logger.success(f"Oracle Output @ {output_utxo} @ Timestamp: {timestamp}")
