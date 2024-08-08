from src.utxo.batcher_utxo_manager import BatcherUTxOManager
from src.utxo.data_utxo_manager import DataUTxOManager
from src.utxo.oracle_utxo_manager import OracleUTxOManager
from src.utxo.queue_utxo_manager import QueueUTxOManager
from src.utxo.reference_utxo_manager import ReferenceUTxOManager
from src.utxo.sale_utxo_manager import SaleUTxOManager
from src.utxo.vault_utxo_manager import VaultUTxOManager


class UTxOManager:
    def __init__(self, batcher_info: dict, data_info: dict, oracle_info: dict, vault_info: dict, reference_info: dict) -> None:
        self.batcher = BatcherUTxOManager(batcher_info)
        self.data = DataUTxOManager(data_info)
        self.oracle = OracleUTxOManager(oracle_info)
        self.queue = None  # is set when its known
        self.reference = ReferenceUTxOManager(reference_info)
        self.sale = None  # is set when its known
        self.vault = VaultUTxOManager(vault_info)

    def set_queue(self, queue_info: dict) -> None:
        self.queue = QueueUTxOManager(queue_info)

    def set_sale(self, sale_info: dict) -> None:
        self.sale = SaleUTxOManager(sale_info)
