class RabbitRegistry:
    def __init__(self):
        self._bindings = set()

    def register(self, binding):
        self._bindings.add(binding)

    def unregister(self, binding):
        self._bindings.remove(binding)

    def list_bindings(self):
        return list(self._bindings)


rabbit_registry = RabbitRegistry()
