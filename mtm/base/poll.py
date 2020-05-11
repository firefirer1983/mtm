import abc


class Poll(abc.ABC):
    @abc.abstractmethod
    def get_interval(self):
        pass

    @abc.abstractmethod
    def set_interval(self, interval):
        pass

    @abc.abstractmethod
    def run(self):
        pass
