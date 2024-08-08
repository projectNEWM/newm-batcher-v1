from src.value import Value

from .base_db_manager import BaseDbManager


class ReferenceDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for reference records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS reference (
                    id TEXT PRIMARY KEY,
                    txid TEXT,
                    cborHex TEXT,
                    value TEXT
                )
            """)

    def load(self, config):
        conn = self.get_connection()
        try:
            conn.execute(
                'INSERT OR IGNORE INTO reference (id, txid, datum, value) VALUES (?, ?, ?, ?)',
                ("unique_", txid, cborHex, value_json)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self, reference):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT txid, cborHex, value FROM reference WHERE id = ?', (reference,))
            record = cursor.fetchone()  # there is only one
            if record:
                txid, cborHex, value_json = record
                value = self.json_to_dict(value_json)
                return {'txid': txid, 'cborHex': cborHex, 'value': Value(value)}
            return None
        finally:
            conn.close()
