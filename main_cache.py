import os
import math
import numpy as np
from typing import Tuple
from tqdm import tqdm

from cache import LineDataWayCache
from decoder import InstructionDecoder
from actions import Action

def factory(cs, bs, w, b = 32) -> Tuple[LineDataWayCache, InstructionDecoder]:

    # rename all parameters using me-style
    size_cache_total_kb = cs
    size_data_cache_b = bs
    n_ways = w
    bits_address = b

    del cs, bs, w, b

    size_cache_total_b = 1024 * size_cache_total_kb
    num_lines_total = int(size_cache_total_b / size_data_cache_b)

    if n_ways == 0:
        num_line_per_way = 1
        n_ways = num_lines_total
    else:
        num_line_per_way = int(num_lines_total / n_ways)
    # end

    # address = { tag | index | offset }
    bits_index = int(math.log(num_line_per_way, 2))
    bits_offset = int(math.log(size_data_cache_b, 2))
    bits_tag = bits_address - bits_index - bits_offset

    cache = LineDataWayCache(num_line_per_way, size_data_cache_b, n_ways, bits_tag)
    decoder = InstructionDecoder(bits_tag, bits_index, bits_offset)

    return cache, decoder
# end



if __name__ == "__main__":

    path_base = 'data'
    i = 'gcc-1K.memtrace'
    path_data = os.path.join(path_base, i)

    cs = 32
    bs = 16  # bs = 2^bits_bs
    w = 4
    cache, decoder = factory(cs, bs, w)

    # str_instruction = 'L 8 12ff228'
    # action = decoder.decode(str_instruction)
    # exit(0)

    with open(path_data,'r') as file:
        strs_instruction = file.read().splitlines()
        for str_instruction in strs_instruction:
        # for str_instruction in tqdm(strs_instruction):
        # for i, str_instruction in enumerate(strs_instruction[:]):
        #     print('[{}]: {}'.format(i, str_instruction))
            action = decoder.decode(str_instruction)
            action.execute(cache)
        # end
    # end

    print(Action.counted_action)
    print(Action.counted_miss)
    print('miss rate: {}'.format(Action.counted_miss/sum(Action.counted_action.values())))
# end