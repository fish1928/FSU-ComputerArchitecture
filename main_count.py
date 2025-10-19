import os
import math
import numpy as np
from typing import Tuple
from tqdm import tqdm
from collections import defaultdict

from cache import LineDataWayCache
from decoder import InstructionDecoder
from actions import Action
from factory import generate_components
import json




if __name__ == "__main__":

    path_base = 'data'
    i = 'gcc-1K.memtrace'
    path_data = os.path.join(path_base, i)

    cs = 128
    bs = 16  # bs = 2^bits_bs
    w = 1
    v = 2

    cache, victim, decoder = generate_components(cs, bs, w, v)

    list_state = []

    with open(path_data,'r') as file:
        strs_instruction = file.read().splitlines()
        for str_instruction in strs_instruction:
        # for str_instruction in tqdm(strs_instruction):
        # for i, str_instruction in enumerate(strs_instruction[:]):
        #     print('[{}]: {}'.format(i, str_instruction))
            action = decoder.decode(str_instruction)
            action.execute(cache, victim)
            list_state.append(action.inspect())
        # end
    # end

    dict_indexoffset_dict_tag_count = {}
    for state in list_state:
        key = '{}-{}'.format(state['index'], state['offset'])
        if key not in dict_indexoffset_dict_tag_count:
            dict_indexoffset_dict_tag_count[key] = defaultdict(int)
        # end
    # end

    for state in list_state:
        key = '{}-{}'.format(state['index'], state['offset'])
        dict_indexoffset_dict_tag_count[key][state['tag']] += 1
    # end

    for key, dict_tag_count in dict_indexoffset_dict_tag_count.items():
        if len(dict_tag_count.keys()) > 1:
            print(key, dict_tag_count)
        # end
    # end

    count_hit = 0
    for key, dict_tag_count in dict_indexoffset_dict_tag_count.items():
        for tag, count in dict_tag_count.items():
            count_hit += (count-1)
        # end
    # end

    print('count_hit: {}'.format(count_hit))
    print('miss rate: {}'.format(Action.counted_miss/sum(Action.counted_action.values())))

# end