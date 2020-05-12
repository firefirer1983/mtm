import pika


class BlockingConnection:
    def __init__(self, url):
        self._url = url
        self._connection = pika.BlockingConnection(
            parameters=pika.URLParameters(self._url),
        )
        self._rabbit_channel = self._connection.channel()

    def poll_event(self):
        self._connection.process_data_events()

    @property
    def channel(self):
        return self._rabbit_channel
