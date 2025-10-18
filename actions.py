from abc import ABCMeta, abstractmethod
from collections import defaultdict

from cache import LineDataWayCache


class Action:

    index_type_action = {}
    counted_action = defaultdict(int)
    counted_miss = 0

    def __init__(self, tag: int, index: int, offset: int):
        self.tag = tag
        self.index = index
        self.offset = offset

        # print('action {}, tag:{} index:{} offset:{}'.format(self.__class__.__name__, self.tag, self.index, self.offset))
        Action.counted_action[self.__class__.__name__] += 1
    # end

    def inspect(self):
        return {
            'tag': self.tag,
            'index': self.index,
            'offset': self.offset,
            'action': str(self.__class__).split('.')[-1][0]
        }
    # end

    @classmethod
    def add_miss(cls):
        cls.counted_miss += 1
    # end

    @classmethod
    def get_miss_count(cls):
        return cls.counted_miss
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

    @abstractmethod
    def execute(self, cache: LineDataWayCache):
        pass
   # end

    def __str__(self):
        return '{} {} {} {}'.format(str(self.__class__).split('.')[-1][0], self.tag, self.index, self.offset)
    # end
# end

class LoadAction(Action):

    @classmethod
    def register_action(cls):
        return 'L'
    # end

    def execute(self, cache: LineDataWayCache):
        indicate_miss = cache.load(self.index, self.offset, self.tag)
        if cache.is_a_miss(indicate_miss):
            Action.add_miss()
            cache.store_direct(self.index, self.offset, self.tag)
        # end
    # end
# end

class StoreAction(Action):

    @classmethod
    def register_action(cls):
        return 'S'
    # end

    def execute(self, cache: LineDataWayCache):
        indicate_miss = cache.store(self.index, self.offset, self.tag)
        if cache.is_a_miss(indicate_miss):
            Action.add_miss()
        # end
    # end
# end