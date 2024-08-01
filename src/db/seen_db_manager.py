from .base_db_manager import BaseDbManager


class SeenDbManager(BaseDbManager):
    def initialize(self):
        # Initialize database tables
        with self.conn:
            # Table for the seen records
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS seen (
                    id TEXT PRIMARY KEY,
                    tag TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def create(self, id: str):
        conn = self.get_connection()
        try:
            conn.execute('INSERT OR REPLACE INTO seen (id, tag) VALUES (?, ?)', (id, id))
            conn.commit()
        finally:
            conn.close()

    def read(self, id: str) -> bool:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM seen WHERE id = ?', (id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()
