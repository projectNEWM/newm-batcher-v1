import json
import sqlite3


class BaseDbManager:
    def __init__(self, db_file='batcher.db'):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def cleanup(self):
        conn = self.get_connection()
        try:
            conn.commit()
        finally:
            conn.close()

    def dict_to_json(self, dict_data):
        return json.dumps(dict_data)

    def json_to_dict(self, json_data):
        return json.loads(json_data)
