class SingletonMixin:
    """A mixin that turns any subclass into a singleton."""
    _singleton_instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._singleton_instances:
            instance = super().__new__(cls)
            cls._singleton_instances[cls] = instance
        return cls._singleton_instances[cls]