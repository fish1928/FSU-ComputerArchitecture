import os
import math
import numpy as np
from typing import Tuple
from tqdm import tqdm
from collections import defaultdict

from cache import LineDataWayCache, VictimCache
from decoder import InstructionDecoder
from actions import Action
import json


def generate_components(cs, bs, w, v=0, b = 32) -> Tuple[LineDataWayCache, VictimCache, InstructionDecoder]:

    # rename all parameters using me-style
    size_cache_total_kb = cs
    size_data_cache_b = bs
    n_ways = w
    n_ways_victim = v
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
    victim = VictimCache(n_ways_victim, bits_tag) if n_ways_victim > 0 else None
    decoder = InstructionDecoder(bits_tag, bits_index, bits_offset)

    return cache, victim, decoder
# end