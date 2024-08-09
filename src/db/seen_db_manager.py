from .base_db_manager import BaseDbManager


class SeenDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for the seen records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS seen (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    queue_txid TEXT,
                    start_time INTEGER,
                    end_time INTEGER
                )
            """)

    def create(self, queue_txid: str, start_time: int, end_time: int):
        conn = self.get_connection()
        try:
            conn.execute(
                'INSERT OR REPLACE INTO seen (queue_txid, start_time, end_time) VALUES (?, ?, ?)',
                (queue_txid, start_time, end_time))
            conn.commit()
        finally:
            conn.close()

    def exists(self, txid: str) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM seen WHERE queue_txid = ? LIMIT 1',
                (txid,)
            )
            record = cursor.fetchone()
            return record is not None
        finally:
            conn.close()

    def delete(self, current_time: int):
        conn = self.get_connection()
        try:
            conn.execute(
                'DELETE FROM seen WHERE end_time <= ?',
                (current_time,)
            )
            conn.commit()
        finally:
            conn.close()
