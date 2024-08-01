import copy


class SaleUTxOManager:
    def __init__(self, data: dict):
        self._data = data

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
