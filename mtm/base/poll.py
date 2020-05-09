import abc


class Poll(abc.ABC):
    def __init__(self, channel, db):
        self._poll_interval = 500
        self._channel = channel
        self._db = db

    @abc.abstractmethod
    def poll(self):
        pass

    @property
    def poll_interval(self):
        return self._poll_interval

    def set_poll_interval(self, interval):
        self._poll_interval = interval

    def run(self):
        self._channel.install_poll(self.poll, self._poll_interval)
        self._channel.run()

    @property
    def channel(self):
        return self._channel

    @property
    def db(self):
        return self._db
