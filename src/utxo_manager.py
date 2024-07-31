from utxo.batcher_utxo_manager import BatcherUTxOManager
from utxo.data_utxo_manager import DataUTxOManager
from utxo.oracle_utxo_manager import OracleUTxOManager
from utxo.queue_utxo_manager import QueueUTxOManager
from utxo.sale_utxo_manager import SaleUTxOManager
from utxo.vault_utxo_manager import VaultUTxOManager


class UTxOManager:
    def __init__(self, batcher_info: dict, data_info: dict, oracle_info: dict, queue_info: dict, sale_info: dict, vault_info: dict) -> None:
        self.batcher = BatcherUTxOManager(batcher_info)
        self.data = DataUTxOManager(data_info)
        self.oracle = OracleUTxOManager(oracle_info)
        self.queue = QueueUTxOManager(queue_info)
        self.sale = SaleUTxOManager(sale_info)
        self.vault = VaultUTxOManager(vault_info)
