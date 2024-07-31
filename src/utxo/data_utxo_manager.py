class DataUTxOManager:
    def __init__(self, data: dict):
        self._data = data

    @property
    def txid(self):
        return self._data.get('txid')

    @property
    def datum(self):
        return self._data.get('datum')
