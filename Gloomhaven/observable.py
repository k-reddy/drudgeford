class Observable:
    def __init__(self):
        self.observers = {}

    def add_observer(self, event: str, method):
        if event not in self.observers:
            self.observers[event] = []
        self.observers[event].append(method)
        print(self.observers)

    def notify_observers(self, event, data):
        for method in self.observers[event]:
            method(data)
