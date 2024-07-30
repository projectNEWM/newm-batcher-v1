from .base_db_manager import BaseDbManager


class OracleDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for oracle records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS oracle (
                    tag TEXT PRIMARY KEY,
                    txid TEXT,
                    datum TEXT,
                    value TEXT
                )
            """)
