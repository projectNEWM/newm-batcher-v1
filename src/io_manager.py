from loguru import Logger

from src.db_manager import DbManager
from src.utility import sha3_256

# from src.parse import asset_list_to_value


class IOManager:
    ###########################################################################
    # Inputs
    ###########################################################################

    @staticmethod
    def batcher_input(db: DbManager, data: dict, logger: Logger) -> None:
        # the tx hash of this transaction
        input_utxo = data['tx_input']['tx_id'] + '#' + str(data['tx_input']['index'])

        # sha3_256 hash of the input utxo
        utxo_base_64 = sha3_256(input_utxo)
        if db.delete_batcher(utxo_base_64):
            logger.success(f"Spent Batcher Input @ {input_utxo} @ Timestamp {data['context']['timestamp']}")
        else:
            logger.warning(f"Can Not Delete Batcher Input @ {input_utxo} @ Timestamp {data['context']['timestamp']}")

    @staticmethod
    def sale_input(db: DbManager, data: dict, logger: Logger) -> None:
        # the tx hash of this sale transaction
        input_utxo = data['tx_input']['tx_id'] + '#' + str(data['tx_input']['index'])

        if db.delete_sale_by_txid(input_utxo):
            logger.success(f"Spent Sale Input @ {input_utxo} @ Timestamp {data['context']['timestamp']}")
        else:
            logger.warning(f"Can Not Delete Sale Input @ {input_utxo} @ Timestamp {data['context']['timestamp']}")

    @staticmethod
    def queue_input(db: DbManager, data: dict, logger: Logger) -> None:
        # the tx hash of this transaction
        input_utxo = data['tx_input']['tx_id'] + '#' + str(data['tx_input']['index'])

        utxo_base_64 = sha3_256(input_utxo)
        if db.delete_queue_by_tag(utxo_base_64):
            logger.success(f"Spent Queue Input: {input_utxo} @ Timestamp {data['context']['timestamp']}")
        else:
            logger.warning(f"Can Not Delete Queue Input: {input_utxo} @ Timestamp {data['context']['timestamp']}")
    ###########################################################################
    # Outputs
    ###########################################################################
