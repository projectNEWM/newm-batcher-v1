from src.value import Value

from .base_db_manager import BaseDbManager


class BatcherDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for batcher records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS batcher (
                    tag TEXT PRIMARY KEY,
                    txid TEXT,
                    value TEXT
                )
            """)

    def create(self, tag, txid, value):
        conn = self.get_connection()
        try:
            value_json = value.dump()
            conn.execute(
                'INSERT OR REPLACE INTO batcher (tag, txid, value) VALUES (?, ?, ?)',
                (tag, txid, value_json)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self, batcher_policy):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT tag, txid, value FROM batcher')
            records = cursor.fetchall()
            for record in records:
                tag, txid, value_json = record
                value = Value(self.json_to_data(value_json))
                if value.exists(batcher_policy):
                    return {'tag': tag, 'txid': txid, 'value': value}
            return None
        finally:
            conn.close()

    def read_all(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT tag, txid, value FROM batcher')
            records = cursor.fetchall()
            batcher_records = []
            for record in records:
                tag, txid, value_json = record
                value = self.json_to_data(value_json)
                batcher_records.append({'tag': tag, 'txid': txid, 'value': Value(value)})
            return batcher_records
        finally:
            conn.close()

    def delete(self, tag):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Check if the record exists
            cursor.execute('SELECT EXISTS(SELECT 1 FROM batcher WHERE tag = ?)', (tag,))
            exists = cursor.fetchone()[0]
            if exists:
                # If the record exists, delete it
                cursor.execute('DELETE FROM batcher WHERE tag = ?', (tag,))
                conn.commit()
                return True  # Record existed and was deleted
            else:
                return False  # Record did not exist
        finally:
            conn.close()
