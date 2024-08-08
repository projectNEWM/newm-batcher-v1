from src.db.batcher_db_manager import BatcherDbManager
from src.db.data_db_manager import DataDbManager
from src.db.oracle_db_manager import OracleDbManager
from src.db.queue_db_manager import QueueDbManager
from src.db.reference_db_manager import ReferenceDbManager
from src.db.sale_db_manager import SaleDbManager
from src.db.seen_db_manager import SeenDbManager
from src.db.status_db_manager import StatusDbManager
from src.db.vault_db_manager import VaultDbManager
from src.value import Value


class DbManager:
    def __init__(self, db_file='batcher.db'):
        self.batcher = BatcherDbManager(db_file)
        self.data = DataDbManager(db_file)
        self.oracle = OracleDbManager(db_file)
        self.queue = QueueDbManager(db_file)
        self.reference = ReferenceDbManager(db_file)
        self.sale = SaleDbManager(db_file)
        self.seen = SeenDbManager(db_file)
        self.status = StatusDbManager(db_file)
        self.vault = VaultDbManager(db_file)

    def initialize(self, config):
        self.batcher.initialize()
        self.data.initialize()
        self.oracle.initialize()
        self.queue.initialize()
        self.reference.initialize()
        self.sale.initialize()
        self.seen.initialize()
        self.status.initialize()
        self.vault.initialize()
        # load the start status from config
        self.status.load(config)
        # load the reference data here
        self.reference.load(config)
        # create the start oracle from empty
        self.oracle.create("", {}, Value({}))
        # create the start data from empty
        self.data.create("", {}, Value({}))

    def cleanup(self):
        self.batcher.cleanup()
        self.data.cleanup()
        self.oracle.cleanup()
        self.queue.cleanup()
        self.reference.cleanup()
        self.sale.cleanup()
        self.seen.cleanup()
        self.status.cleanup()
        self.vault.cleanup()
