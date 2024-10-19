class Observable:
    def __init__(self):
        self.observers = {}

    def add_observer(self, key: str, method):
        if key not in self.observers:
            self.observers[key] = []
        self.observers[key].append(method)

    def notify_observers(self, key, data):
        for method in self.observers[key]:
            method(data)
