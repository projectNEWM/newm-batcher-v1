from .base_db_manager import BaseDbManager


class OracleDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for oracle records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS oracle (
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
                'INSERT OR IGNORE INTO oracle (id, txid, datum) VALUES (?, ?, ?)',
                ("unique_oracle", txid, datum_json)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT txid, datum FROM oracle WHERE id = ?', ("unique_oracle",))
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
                'UPDATE oracle SET txid = ?, datum = ? WHERE id = ?',
                (txid, datum_json, "unique_oracle")
            )
            conn.commit()
        finally:
            conn.close()
