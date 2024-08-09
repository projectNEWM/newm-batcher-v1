from src.value import Value

from .base_db_manager import BaseDbManager


class SaleDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for sale records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS sale (
                    tkn TEXT PRIMARY KEY,
                    txid TEXT,
                    datum TEXT,
                    value TEXT
                )
            """)

    def create(self, tkn, txid, datum, value):
        conn = self.get_connection()
        try:
            datum_json = self.data_to_json(datum)
            value_json = value.dump()
            conn.execute(
                'INSERT OR REPLACE INTO sale (tkn, txid, datum, value) VALUES (?, ?, ?, ?)',
                (tkn, txid, datum_json, value_json)
            )
            conn.commit()
        finally:
            conn.close()

    def read(self, tkn):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT txid, datum, value FROM sale WHERE tkn = ?', (tkn,))
            record = cursor.fetchone()
            if record:
                txid, datum_json, value_json = record
                datum = self.json_to_data(datum_json)
                value = self.json_to_data(value_json)
                return {'txid': txid, 'datum': datum, 'value': Value(value)}
            return None
        finally:
            conn.close()

    def read_all(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # lexicographical ordering for sales.
            cursor.execute('SELECT tkn FROM sale ORDER BY tkn')
            records = cursor.fetchall()
            sale_records = []
            for record in records:
                tkn = record[0]  # only tkn is there (tkn, )
                sale_records.append(tkn)
            return sale_records
        finally:
            conn.close()

    def delete(self, txid):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Check if the record exists with the given txid
            cursor.execute('SELECT EXISTS(SELECT 1 FROM sale WHERE txid = ?)', (txid,))
            exists = cursor.fetchone()[0]
            if exists:
                # If the record exists, delete it
                cursor.execute('DELETE FROM sale WHERE txid = ?', (txid,))
                conn.commit()
                return True  # Record with the given txid existed and was deleted
            else:
                return False  # No record with the given txid
        finally:
            conn.close()
