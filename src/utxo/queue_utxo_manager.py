import copy


class QueueUTxOManager:
    def __init__(self, data: dict):
        self._data = data

    @property
    def tag(self):
        return self._data.get('tag')

    @property
    def tkn(self):
        return self._data.get('tkn')

    @property
    def timestamp(self):
        return self._data.get('timestamp')

    @property
    def tx_idx(self):
        return self._data.get('tx_idx')

    @property
    def txid(self):
        return self._data.get('txid')

    @txid.setter
    def txid(self, value):
        self._data['txid'] = value

    @property
    def datum(self):
        return self._data.get('datum')

    @property
    def value(self):
        return self._data.get('value')

    @value.setter
    def value(self, new_value):
        self._data['value'] = copy.deepcopy(new_value)
