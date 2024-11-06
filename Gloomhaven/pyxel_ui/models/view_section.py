import abc

class ViewSection(abc.ABC):
    @abc.abstractmethod
    def __init__(self, pyxel):
        self.pyxel = pyxel

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass
