import abc


class MessageConsumer(abc.ABC):
    @abc.abstractmethod
    def on_message(self, *args, body):
        pass


class MessageProducer(abc.ABC):
    @abc.abstractmethod
    def publish_message(self, *args, **kwargs):
        pass
