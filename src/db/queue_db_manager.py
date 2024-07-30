from src.value import Value

from .base_db_manager import BaseDbManager


class QueueDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for queue records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    tag TEXT PRIMARY KEY,
                    txid TEXT,
                    tkn TEXT,
                    datum TEXT,
                    value TEXT,
                    timestamp INTEGER,
                    tx_idx INTEGER
                )
            """)

    def create(self, tag, txid, tkn, datum, value, timestamp, tx_idx):
        conn = self.get_connection()
        try:
            datum_json = self.dict_to_json(datum)
            value_json = value.dump()
            conn.execute(
                'INSERT OR REPLACE INTO queue (tag, txid, tkn, datum, value, timestamp, tx_idx) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (tag, txid, tkn, datum_json, value_json, timestamp, tx_idx)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self, tag):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT txid, tkn, datum, value, timestamp, tx_idx FROM queue WHERE tag = ?', (tag,))
            record = cursor.fetchone()
            if record:
                txid, tkn, datum_json, value_json, timestamp, tx_idx = record
                datum = self.json_to_dict(datum_json)
                value = self.json_to_dict(value_json)
                return {'tag': tag, 'txid': txid, 'tkn': tkn, 'datum': datum, 'value': Value(value), 'timestamp': timestamp, 'tx_idx': tx_idx}
            return None
        finally:
            conn.close()

    def read_all(self, pointer: str):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT tag, txid, tkn, datum, value, timestamp, tx_idx FROM queue WHERE tkn = ?', (pointer,))
            records = cursor.fetchall()
            queue_records = []
            for record in records:
                tag, txid, tkn, datum_json, value_json, timestamp, tx_idx = record
                datum = self.json_to_dict(datum_json)
                value = self.json_to_dict(value_json)
                queue_records.append((tag, {'tag': tag, 'txid': txid, 'tkn': tkn, 'datum': datum, 'value': Value(value), 'timestamp': timestamp, 'tx_idx': tx_idx}))
            return queue_records
        finally:
            conn.close()

    # get all queue records by tkn

    def delete(self, tag):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Check if the record exists with the given txid
            cursor.execute('SELECT EXISTS(SELECT 1 FROM queue WHERE tag = ?)', (tag,))
            exists = cursor.fetchone()[0]
            if exists:
                # If the record exists, delete it
                cursor.execute('DELETE FROM queue WHERE tag = ?', (tag,))
                conn.commit()
                return True  # Record with the given txid existed and was deleted
            else:
                return False  # No record with the given txid
        finally:
            conn.close()
