from src.db.sale_db_manager import SaleDbManager
from src.db.seen_db_manager import SeenDbManager


class DbManager:
    def __init__(self, db_file='batcher.db'):
        self.seen = SeenDbManager(db_file)
        self.sale = SaleDbManager(db_file)

    def initialize(self):
        self.seen.initialize()
        self.sale.initialize()

    def cleanup(self):
        self.seen.cleanup()
        self.sale.cleanup()
