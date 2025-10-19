import os
import sys
import argparse
from dataclasses import dataclass

from actions import Action
from factory import generate_components

@dataclass
class Config:
    BS_VALID = [2,4,8,16,32,64]
    WAYS_VALID = [0,1,2,4,8,16]
    CS_RANGE_VALID = range(1,4096+1)
    VICTIM_RANGE_VALID = range(1, 1024+1)

    i: str
    cs: int
    bs: int
    w: int
    v: int = 0
# end

def generate_parser():
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='Cache simulator parameters',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-i', required=True, type=str, help='Input file')
    parser.add_argument('-cs', required=True, type=int, choices=Config.CS_RANGE_VALID, metavar='[1-4096]', help='Total Cache Size(KB)')
    parser.add_argument('-bs', required=True, type=int, choices=Config.BS_VALID, help='Cache Block Size(B), {}'.format(Config.BS_VALID))
    parser.add_argument('-w', required=True, type=int, choices=Config.WAYS_VALID, help='Number of Ways {}, 0: fully associate, 1: direct mapping'.format(Config.WAYS_VALID))
    parser.add_argument('-v', type=int, choices=Config.VICTIM_RANGE_VALID, metavar='[1-1024]',help='(Optional) Victim Cache Size(lines)')

    return parser
# end

def parse_args(argv: list[str]) -> Config:
    parser = generate_parser()
    args = parser.parse_known_args(argv)[0]

    config = Config(
        i=args.i,
        cs=args.cs,
        bs=args.bs,
        w=args.w
    )
    if args.v:
        config.v = args.v
    # end

    return config
# end


def main(argv):
    config = parse_args(argv)

    i = config.i
    cs = config.cs
    bs = config.bs
    w = config.w
    v = config.v

    cache, victim, decoder = generate_components(cs, bs, w, v)
    with open(i,'r') as file:
        strs_instruction = file.read().splitlines()
        for str_instruction in strs_instruction:
            action = decoder.decode(str_instruction)
            action.execute(cache, victim)
        # end
    # end

    count_miss = Action.counted_miss
    count_all = sum(Action.counted_action.values())
    count_hit = count_all - count_miss
    rate_miss = count_miss / count_all

    bits_index = decoder.bits_index
    bits_offset = decoder.bits_offset
    bits_tag = decoder.bits_tag

    # prepare to print
    annotation_way = None
    match w:
        case 0:
            annotation_way = 'fully-associative'
        case 1:
            annotation_way = 'direct-mapped associativity'
        case _:
            annotation_way = 'Number of ways = {}'.format(w)
        # end
    # end


    print('**********************')
    print('file name: {}'.format(i))
    print('Cache Size = {} KB'.format(cs))
    print('Block Size = {} B'.format(bs))
    print(annotation_way)
    print('Number of Victim Cache = {}'.format(v))
    print('numOfOffsetBits = {}'.format(bits_offset))
    print('numOfIndexBits = {}'.format(bits_index))
    print('numOfTagBits = {}'.format(bits_tag))
    print()
    print('Cache hit count = {}'.format(count_hit))
    print('Cache miss count = {}'.format(count_miss))
    print('Instruction count = {}'.format(count_all))
    print('Cache miss rate = {:0.2f}%'.format(rate_miss*100))
    print('**********************')
# end





if __name__ == "__main__":
    main(sys.argv)
# end