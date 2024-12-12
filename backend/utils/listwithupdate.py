class ListWithUpdate:
    def __init__(self, data, *callables):
        self.data = data
        self.to_call = callables

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value
        self._call_updates()

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return repr(self.data)

    def append(self, item):
        self.data.append(item)
        self._call_updates()

    def remove(self, item):
        self.data.remove(item)
        self._call_updates()
    
    def clear(self):
        self.data.clear()
        self._call_updates()

    def _call_updates(self):
        for func in self.to_call:
            func(self.data)


# use lambdas to encode arguments or functools.partial
