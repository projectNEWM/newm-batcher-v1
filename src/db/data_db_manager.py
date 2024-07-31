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
                    datum TEXT
                )
            """)

    def create(self, txid, datum):
        conn = self.get_connection()
        try:
            datum_json = self.dict_to_json(datum)
            conn.execute(
                'INSERT OR IGNORE INTO data (id, txid, datum) VALUES (?, ?, ?)',
                ("unique_data", txid, datum_json)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT txid, datum FROM data WHERE id = ?', ("unique_data",))
            record = cursor.fetchone()  # there is only one
            if record:
                txid, datum_json = record
                datum = self.json_to_dict(datum_json)
                return {'txid': txid, 'datum': datum}
            return None
        finally:
            conn.close()

    def update(self, txid, datum):
        # it only gets created once, so the id is always known
        conn = self.get_connection()
        try:
            datum_json = self.dict_to_json(datum)
            conn.execute(
                'UPDATE data SET txid = ?, datum = ? WHERE id = ?',
                (txid, datum_json, "unique_data")
            )
            conn.commit()
        finally:
            conn.close()
