import math
import numpy as np
from typing import Tuple

from lru_module import NwayLRU

class LineDataWayCache:

    INDICATE_MISS = -1

    def is_a_miss(self, indicate_target):
        return indicate_target == self.__class__.INDICATE_MISS
    # end

    def __init__(self, num_line_per_way, size_data_cache_b, n_ways, bits_tag):

        bits_np = int(math.pow(2, math.ceil(math.log(bits_tag, 2))))
        if bits_np > 64:
            raise Exception()
        # end
        str_type_np = 'uint{}'.format(bits_np)

        self.num_line_per_way = num_line_per_way
        self.size_data_cache_b = size_data_cache_b
        self.n_ways = n_ways
        self.bits_tag = bits_tag
        self.str_type_np = str_type_np

        print('initialize cache with {} {} {} {}'.format(num_line_per_way, size_data_cache_b, n_ways, str_type_np))
        self.cache = np.zeros((num_line_per_way, size_data_cache_b, n_ways), dtype=str_type_np)  # save tags
        self.lru = NwayLRU(num_line_per_way, n_ways)
        print('initialize lru module with {}'.format(self.lru.shape()))
    # end

    def shape(self):
        return self.cache.shape
    # end

    def lookup(self, index, offset, tag):
        data_ways_all = self.cache[index][offset]   # size->(n_ways,)
        indicates_hit = np.where(data_ways_all == tag)[0]
        indicate_target = self.__class__.INDICATE_MISS if indicates_hit.size == 0 else indicates_hit[0]
        return indicate_target, self.lru.get_least(index)
    # end

    def touch(self, index, indicate_target):    # touch no offset (LRU for line)
        self.lru.touch(index, indicate_target)
    # end

    def store_direct(self, index, offset, tag, indicate_target):
        data_ways_all = self.cache[index][offset]   # size->(n_ways,)
        tag_removed = data_ways_all[indicate_target]
        data_ways_all[indicate_target] = tag

        self.touch(index, indicate_target)
        return tag_removed
    # end

    # def load_v1(self, index, offset, tag):
    #     data_ways_all = self.cache[index][offset]   # size->(n_ways,)
    #     indicates_hit = np.where(data_ways_all == tag)[0]
    #     if indicates_hit.size == 0: # is miss
    #         return self.__class__.INDICATE_MISS # return and do nothing
    #     else:                    # is hit
    #         self.lru.use(index, indicates_hit[0])  # use the first(logically) hit
    #         return indicates_hit[0]
    #     # end
    # # end

    # def store_v1(self, index, offset, tag) -> Tuple[int, int]:

    #     data_ways_all = self.cache[index][offset]   # size->(n_ways,)
    #     indicates_hit = np.where(data_ways_all == tag)[0]
        
    #     if indicates_hit.size == 0: # is miss when updating
    #         indicate_least_use = self.lru.find_and_replace(index)
    #         tag_removed = data_ways_all[indicate_least_use]
    #         data_ways_all[indicate_least_use] = tag     # MARK: potential swipe
    #         return self.__class__.INDICATE_MISS, tag_removed
    #     else:                       # is hit
    #         self.lru.use(index, indicates_hit[0])
    #         return indicates_hit[0], 0
    #     # end
    # # end

    # def store_direct_old(self, index, offset, tag):
    #     data_ways_all = self.cache[index][offset]   # size->(n_ways,)
    #     indicate_least_use = self.lru.find_and_replace(index)
    #     tag_removed = data_ways_all[indicate_least_use]
    #     data_ways_all[indicate_least_use] = tag     # MARK: potential swipe
    #     return tag_removed
    # # end

    # def store_direct_v1(self, index, offset, tag):
    #     data_ways_all = self.cache[index][offset]   # size->(n_ways,)
    #     indicate_least_use = self.lru.find_and_replace(index)
    #     tag_removed = data_ways_all[indicate_least_use]
    #     data_ways_all[indicate_least_use] = tag     # MARK: potential swipe
    #     return tag_removed
    # # end
# end

class VictimCache(LineDataWayCache):

    NUM_LINE_PER_WAY_DEFAULT = 1
    INDEX_VICTIM_DEFAULT = 0

    SIZE_DATA_CACHE_B_DEFAULT = 1
    OFFSET_VICTIM_DEFAULT = 0


    def __init__(self, n_ways_victim, bits_tag):
        super().__init__(VictimCache.NUM_LINE_PER_WAY_DEFAULT, VictimCache.SIZE_DATA_CACHE_B_DEFAULT, n_ways_victim, bits_tag)
    # end

    def lookup(self, tag):
        print('VictimCache.lookup {}'.format(tag))
        return super().lookup(VictimCache.INDEX_VICTIM_DEFAULT, VictimCache.OFFSET_VICTIM_DEFAULT, tag)
    # end

    def store_direct(self, tag, indicate_target):
        print('VictimCache.store_direct {}'.format(tag, indicate_target))
        return super().store_direct(VictimCache.INDEX_VICTIM_DEFAULT, VictimCache.OFFSET_VICTIM_DEFAULT, tag, indicate_target)
    # end