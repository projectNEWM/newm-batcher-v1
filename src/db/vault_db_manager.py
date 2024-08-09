from src.value import Value

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
                    pkh TEXT,
                    datum TEXT,
                    value TEXT
                )
            """)

    def create(self, tag, txid, pkh, datum, value):
        conn = self.get_connection()
        try:
            datum_json = self.dict_to_json(datum)
            value_json = value.dump()
            conn.execute(
                'INSERT OR REPLACE INTO vault (tag, txid, pkh, datum, value) VALUES (?, ?, ?, ?, ?)',
                (tag, txid, pkh, datum_json, value_json)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self, pkh):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT txid, datum, value FROM vault WHERE pkh = ?', (pkh,))
            record = cursor.fetchone()
            if record:
                txid, datum_json, value_json = record
                datum = self.json_to_dict(datum_json)
                value = self.json_to_dict(value_json)
                return {'pkh': pkh, 'txid': txid, 'datum': datum, 'value': Value(value)}
            return None
        finally:
            conn.close()

    def read_all(self, pkh):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT txid, datum, value FROM vault WHERE pkh = ?', (pkh,))
            records = cursor.fetchall()  # Fetch all matching records
            if records:
                results = []
                for record in records:
                    txid, datum_json, value_json = record
                    datum = self.json_to_dict(datum_json)
                    value = self.json_to_dict(value_json)
                    results.append({'pkh': pkh, 'txid': txid, 'datum': datum, 'value': Value(value)})
                return results
            return None
        finally:
            conn.close()

    def delete(self, tag):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Check if the record exists with the given txid
            cursor.execute('SELECT EXISTS(SELECT 1 FROM vault WHERE tag = ?)', (tag,))
            exists = cursor.fetchone()[0]
            if exists:
                # If the record exists, delete it
                cursor.execute('DELETE FROM vault WHERE tag = ?', (tag,))
                conn.commit()
                return True  # Record with the given txid existed and was deleted
            else:
                return False  # No record with the given txid
        finally:
            conn.close()
