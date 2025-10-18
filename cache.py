import math
import numpy as np
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

    def load(self, index, offset, tag):
        data_ways_all = self.cache[index][offset]   # size->(n_ways,)
        indicates_hit = np.where(data_ways_all == tag)[0]
        if indicates_hit.size == 0: # is miss
            return self.__class__.INDICATE_MISS # return and do nothing
        else:                    # is hit
            self.lru.use(index, indicates_hit[0])  # use the first(logically) hit
            return indicates_hit[0]
        # end
    # end

    def store(self, index, offset, tag):
        data_ways_all = self.cache[index][offset]   # size->(n_ways,)
        indicates_hit = np.where(data_ways_all == tag)[0]

        if indicates_hit.size == 0: # is miss when updating
            indicate_least_use = self.lru.find_and_replace(index)
            data_ways_all[indicate_least_use] = tag
            return self.__class__.INDICATE_MISS
        else:                       # is hit
            self.lru.use(index, indicates_hit[0])
            return indicates_hit[0]
        # end
    # end
# end

