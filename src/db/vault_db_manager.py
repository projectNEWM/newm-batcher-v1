from .base_db_manager import BaseDbManager


class VaultDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for vault records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS vault (
                    tag TEXT PRIMARY KEY,
                    txid TEXT,
                    datum TEXT,
                    value TEXT
                )
            """)

    def create(self, tag, txid, datum, value):
        pass

    def read(self, tag):
        pass

    def delete(self, tag):
        pass
