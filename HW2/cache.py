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

        self.cache = np.zeros((num_line_per_way, size_data_cache_b, n_ways), dtype=str_type_np)  # save tags
        self.lru = NwayLRU(num_line_per_way, n_ways)
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

        LineDataWayCache.touch(self, index, indicate_target)    # self.touch might call child function
        return tag_removed
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
        return super().lookup(VictimCache.INDEX_VICTIM_DEFAULT, VictimCache.OFFSET_VICTIM_DEFAULT, tag)
    # end

    def store_direct(self, tag, indicate_target):
        return super().store_direct(VictimCache.INDEX_VICTIM_DEFAULT, VictimCache.OFFSET_VICTIM_DEFAULT, tag, indicate_target)
    # end

    def touch(self, indicate_target):
        return super().touch(VictimCache.INDEX_VICTIM_DEFAULT, indicate_target)
    # end
# end