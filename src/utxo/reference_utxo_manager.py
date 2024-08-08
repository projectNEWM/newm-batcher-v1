class Reference:
    def __init__(self, data: dict):
        self._data = data

    @property
    def txid(self):
        return self._data.get('txid')

    @property
    def cborHex(self):
        return self._data.get('cborHex')

    @property
    def value(self):
        return self._data.get('value')


class ReferenceUTxOManager:
    def __init__(self, data: dict):
        self._sale = Reference(data["sale"])
        self._queue = Reference(data["queue"])
        self._vault = Reference(data["vault"])

    @property
    def sale(self):
        return self._sale

    @property
    def queue(self):
        return self._queue

    @property
    def vault(self):
        return self._vault
