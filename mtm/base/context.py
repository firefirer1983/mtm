import abc


class Context(abc.ABC):
    @abc.abstractmethod
    def add_consumer(self, consumer):
        pass

    @abc.abstractmethod
    def add_producer(self, producer):
        pass

    @abc.abstractmethod
    def remove_consumer(self, consumer_id):
        pass

    @abc.abstractmethod
    def remove_producer(self, producer_id):
        pass
    
    @abc.abstractmethod
    def get_consumer(self, consumer_id):
        pass
    
    @abc.abstractmethod
    def get_producer(self, producer_id):
        pass

