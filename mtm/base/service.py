import abc


class MessageConsumer(abc.ABC):
    @abc.abstractmethod
    def on_message(self, body):
        pass

    @abc.abstractmethod
    def ack_message(self, ack_tag):
        pass


class MessageProducer(abc.ABC):
    @abc.abstractmethod
    def publish_message(self, *args, **kwargs):
        pass


class RpcClient(abc.ABC):
    @abc.abstractmethod
    def call(self, msg):
        pass


class RpcServer(abc.ABC):
    @abc.abstractmethod
    def on_request(self, body):
        pass
