class ListWithUpdate:
    def __init__(self, data, *callables):
        self.data = data
        self.to_call = callables

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value
        callable(self.data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return repr(self.data)

    def append(self, item):
        self.data.append(item)
        callable(item)

    def remove(self, item):
        self.data.remove(item)
        callable(item)


# use lambdas to encode arguments or functools.partial
