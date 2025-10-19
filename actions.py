from abc import ABCMeta, abstractmethod
from collections import defaultdict

from cache import LineDataWayCache, VictimCache


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

# class LoadActionOld(Action):

#     @classmethod
#     def register_action(cls):
#         return 'LOld'
#     # end

#     def execute(self, cache: LineDataWayCache):
#         indicate_miss = cache.load(self.index, self.offset, self.tag)
#         if cache.is_a_miss(indicate_miss):
#             Action.add_miss()
#             cache.store_direct(self.index, self.offset, self.tag)
#         # end
#     # end
# # end

# class StoreActionOld(Action):

#     @classmethod
#     def register_action(cls):
#         return 'SOld'
#     # end

#     def execute(self, cache: LineDataWayCache):
#         indicate_miss, tag_removed = cache.store(self.index, self.offset, self.tag)

#         if cache.is_a_miss(indicate_miss):
#             Action.add_miss()
#         # end
#     # end
# # end

class LoadAction(Action):
    @classmethod
    def register_action(cls):
        return 'L'
    # end

    def execute(self, cache: LineDataWayCache, victim: VictimCache = None):
        indicate_target, indicate_least = cache.lookup(self.index, self.offset, self.tag)
        if not cache.is_a_miss(indicate_target):
            cache.touch(self.index, indicate_target) # -> will update lru
            return
        # end

        # there is a load miss
        if not victim:
            cache.store_direct(self.index, self.offset, self.tag, indicate_least) # -> will update lru
            Action.add_miss()
            return
        # end

        # if victim
        indicate_victim, indicate_victim_least = victim.lookup(self.tag)
        if victim.is_a_miss(indicate_victim):
            tag_removed = cache.store_direct(self.index, self.offset, self.tag, indicate_least) # -> update lru
            if tag_removed:
                print('LoadAction.execute: swiped out {}!!!'.format(self.tag))
                victim.store_direct(tag_removed, indicate_victim_least)                             # -> update lru
            # end
            Action.add_miss()
            return
        # end

        victim.touch(indicate_victim)
    # end
# end


class StoreAction(Action):
    @classmethod
    def register_action(cls):
        return 'S'
    # end

    def execute(self, cache: LineDataWayCache, victim: VictimCache = None):
        indicate_target, indicate_least = cache.lookup(self.index, self.offset, self.tag)
        if not cache.is_a_miss(indicate_target):
            cache.store_direct(self.index, self.offset, self.tag, indicate_target) # -> will update lru
            return
        # end

        # there is a store miss
        if not victim:
            cache.store_direct(self.index, self.offset, self.tag, indicate_least) # -> will update lru
            Action.add_miss()
            return
        # end

        # if victim
        indicate_victim, indicate_victim_least = victim.lookup(self.tag)
        if victim.is_a_miss(indicate_victim):
            tag_removed = cache.store_direct(self.index, self.offset, self.tag, indicate_least) # -> update lru
            if tag_removed:         # swiped out
                print('StoreAction.execute: swiped out {}!!!'.format(self.tag))
                victim.store_direct(tag_removed, indicate_victim_least)                             # -> update lru
            # end
            Action.add_miss()
            return
        # end

        victim.touch(indicate_victim)
    # end
# end