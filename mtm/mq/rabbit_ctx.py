from itertools import chain

from ..base.context import Context


class RabbitContext(Context):
    def __init__(self):
        self._consumers = set()
        self._producers = set()
        self._rpc_clients = set()

    def add_consumer(self, consumer):
        self._consumers.add(consumer)

    def add_producer(self, producer):
        self._producers.add(producer)

    def remove_consumer(self, consumer_id):
        to_remove = None
        for c in list(self._consumers):
            if c.consumer_id == consumer_id:
                to_remove = c
        if to_remove:
            self._consumers.remove(to_remove)

    def remove_producer(self, producer_id):
        to_remove = None
        for c in list(self._producers):
            if c.producer_id == producer_id:
                to_remove = c
        if to_remove:
            self._producers.remove(to_remove)

    def get_consumer(self, consumer_id):
        to_get = None
        for c in list(self._consumers):
            if c.consumer_id == consumer_id:
                to_get = c
        if to_get:
            self._consumers.remove(to_get)

    def get_producer(self, producer_id):
        to_get = None
        for c in list(self._producers):
            if c.producer_id == producer_id:
                to_get = c
        if to_get:
            self._producers.remove(to_get)

    def list_bindings(self):

        return list(
            chain(
                [c.binding for c in self._consumers],
                [p.binding for p in self._producers if not p.binding.is_rpc],
            )
        )


rabbit_context = RabbitContext()
