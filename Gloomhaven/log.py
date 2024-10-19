from observable import Observable


class Log(Observable):
    def __init__(self):
        super().__init__()
        self.observers = {"log": []}
        self.log = []

    def __repr__(self):
        print(self.log)

    def add_observer(self, method):
        return super().add_observer("log", method)

    def add(self, string_to_log):
        self.log.append(string_to_log)
        self.notify_observers("log", string_to_log)
