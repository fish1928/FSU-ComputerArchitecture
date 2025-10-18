from abc import ABCMeta, abstractmethod

class Action:

    index_type_action = {}

    def __init__(self, cache=None):
        self.cache = cache
    # end

    @classmethod
    @abstractmethod
    def register_action(cls):
        pass
    # end

    @classmethod
    def get_action_klass(cls, str_action):
        if str_action in cls.index_type_action:
            return cls.index_type_action[str_action]
        # end

        for subklass in cls.__subclasses__():
            cls.index_type_action[subklass.register_action()] = subklass
        # end

        return cls.index_type_action[str_action] 
    # end
# end

class LoadAction(Action):

    @classmethod
    def register_action(cls):
        return 'L'
    # end

    def execute(self, tag, index, offset):
        pass
    # end

    
# end

class StoreAction(Action):

    @classmethod
    def register_action(cls):
        return 'S'
    # end

    def execute(self, address):
        pass
    # end
# end
