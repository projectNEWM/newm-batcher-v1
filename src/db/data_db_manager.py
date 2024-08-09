from src.value import Value

from .base_db_manager import BaseDbManager


class DataDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for data records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS data (
                    id TEXT PRIMARY KEY,
                    txid TEXT,
                    datum TEXT,
                    value TEXT
                )
            """)

    def create(self, txid, datum, value):
        conn = self.get_connection()
        try:
            datum_json = self.data_to_json(datum)
            value_json = value.dump()
            conn.execute(
                'INSERT OR IGNORE INTO data (id, txid, datum, value) VALUES (?, ?, ?, ?)',
                ("unique_data", txid, datum_json, value_json)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT txid, datum, value FROM data WHERE id = ?', ("unique_data",))
            record = cursor.fetchone()  # there is only one
            if record:
                txid, datum_json, value_json = record
                datum = self.json_to_data(datum_json)
                value = self.json_to_data(value_json)
                return {'txid': txid, 'datum': datum, 'value': Value(value)}
            return None
        finally:
            conn.close()

    def update(self, txid, datum, value):
        # it only gets created once, so the id is always known
        conn = self.get_connection()
        try:
            datum_json = self.data_to_json(datum)
            value_json = value.dump()
            conn.execute(
                'UPDATE data SET txid = ?, datum = ?, value = ? WHERE id = ?',
                (txid, datum_json, value_json, "unique_data")
            )
            conn.commit()
        finally:
            conn.close()
