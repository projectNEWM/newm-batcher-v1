import copy


class OracleUTxOManager:
    def __init__(self, data: dict):
        self._data = data

    @property
    def txid(self):
        return self._data.get('txid')

    @property
    def datum(self):
        return self._data.get('datum')

    @property
    def value(self):
        return self._data.get('value')

    @value.setter
    def value(self, new_value):
        self._data['value'] = copy.deepcopy(new_value)
