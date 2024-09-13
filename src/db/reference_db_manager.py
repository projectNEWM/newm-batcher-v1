import os

import cbor2

from src.tx_simulate import get_cbor_from_file
from src.utility import parent_directory_path
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
        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        # sale
        sale_path = os.path.join(parent_dir, "contracts/sale_contract.plutus")
        sale_double_cbor = get_cbor_from_file(sale_path)
        sale_cbor = cbor2.loads(bytes.fromhex(sale_double_cbor)).hex()

        # queue
        queue_path = os.path.join(parent_dir, "contracts/queue_contract.plutus")
        queue_double_cbor = get_cbor_from_file(queue_path)
        queue_cbor = cbor2.loads(bytes.fromhex(queue_double_cbor)).hex()

        # vault
        vault_path = os.path.join(parent_dir, "contracts/vault_contract.plutus")
        vault_double_cbor = get_cbor_from_file(vault_path)
        vault_cbor = cbor2.loads(bytes.fromhex(vault_double_cbor)).hex()

        try:
            conn.execute(
                'INSERT OR REPLACE INTO reference (id, txid, cborHex, value) VALUES (?, ?, ?, ?)',
                ("sale_reference", config["sale_ref_utxo"], sale_cbor, Value({"lovelace": config["sale_lovelace"]}).dump())
            )
            conn.execute(
                'INSERT OR REPLACE INTO reference (id, txid, cborHex, value) VALUES (?, ?, ?, ?)',
                ("queue_reference", config["queue_ref_utxo"], queue_cbor, Value({"lovelace": config["queue_lovelace"]}).dump())
            )
            conn.execute(
                'INSERT OR REPLACE INTO reference (id, txid, cborHex, value) VALUES (?, ?, ?, ?)',
                ("vault_reference", config["vault_ref_utxo"], vault_cbor, Value({"lovelace": config["vault_lovelace"]}).dump())
            )
            conn.commit()
        finally:
            conn.close()

    def read(self):
        conn = self.get_connection()
        data = {
            "sale": {},
            "queue": {},
            "vault": {},
        }
        try:
            cursor = conn.cursor()
            references = {
                "sale_reference": "sale",
                "queue_reference": "queue",
                "vault_reference": "vault",
            }

            for ref_id, key in references.items():
                cursor.execute('SELECT txid, cborHex, value FROM reference WHERE id = ?', (ref_id,))
                record = cursor.fetchone()  # there is only one
                if record:
                    txid, cborHex, value_json = record
                    value = self.json_to_data(value_json)
                    data[key] = {'txid': txid, 'cborHex': cborHex, 'value': Value(value)}
            return data
        finally:
            conn.close()
