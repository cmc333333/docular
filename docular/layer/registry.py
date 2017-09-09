class _Registry:
    def __init__(self):
        self._registry = {}

    def __setitem__(self, key, value):
        self._registry[key] = value

    def __getitem__(self, key):
        return self._registry[key]


registry = _Registry()
