
#!/usr/bin/env python3
import argparse
import math
from typing import List, Tuple

def ilog2(x: int) -> int:
    if x <= 0 or (x & (x - 1)) != 0:
        raise ValueError(f"value must be a positive power of two, got {x}")
    return x.bit_length() - 1

class LRUSet:
    """
    A single set with LRU replacement.
    We keep a list of tags; rightmost is MRU, leftmost is LRU.
    """
    __slots__ = ("ways", "tags")
    def __init__(self, ways: int):
        self.ways = ways
        self.tags: List[int] = []

    def access(self, tag: int) -> bool:
        """
        Returns True on hit, False on miss. Updates LRU state.
        """
        try:
            idx = self.tags.index(tag)
            # Move to MRU
            t = self.tags.pop(idx)
            self.tags.append(t)
            return True
        except ValueError:
            # Miss: insert (evict LRU if full)
            if len(self.tags) >= self.ways:
                # Evict LRU
                self.tags.pop(0)
            self.tags.append(tag)
            return False

class Cache:
    def __init__(self, cache_kb: int, block_size: int, ways: int):
        if cache_kb <= 1 or cache_kb >= 4096:
            raise ValueError("Total Cache Size (KB) must satisfy 4096 > cs > 1")
        if block_size not in (2,4,8,16,32,64):
            raise ValueError("Block size must be one of {2,4,8,16,32,64} bytes")
        # Compute total number of cache lines/blocks
        total_bytes = cache_kb * 1024
        if total_bytes % block_size != 0:
            raise ValueError("Cache size must be a multiple of block size")
        num_lines = total_bytes // block_size
        if ways == 0:
            # Convention for this homework: w=0 => fully associative (one set)
            ways = num_lines
        if ways not in (1,2,4,8,16,num_lines):
            # Allow fully associative dynamic 'ways == num_lines'
            pass
        if num_lines % ways != 0:
            raise ValueError("Number of lines must be divisible by 'ways'")
        self.block_size = block_size
        self.num_lines = num_lines
        self.ways = ways
        self.num_sets = num_lines // ways
        self.offset_bits = ilog2(block_size)
        self.index_bits = ilog2(self.num_sets) if self.num_sets > 1 else 0
        self.tag_bits = 32 - self.offset_bits - self.index_bits
        # Build sets
        self.sets: List[LRUSet] = [LRUSet(ways) for _ in range(self.num_sets if self.num_sets>0 else 1)]
        # Stats
        self.hits = 0
        self.misses = 0
        self.accesses = 0

    def _split_address(self, addr32: int) -> Tuple[int, int, int]:
        offset_mask = (1 << self.offset_bits) - 1
        index_mask = (1 << self.index_bits) - 1 if self.index_bits > 0 else 0
        offset = addr32 & offset_mask
        index = (addr32 >> self.offset_bits) & index_mask if self.index_bits > 0 else 0
        tag = addr32 >> (self.offset_bits + self.index_bits)
        return tag, index, offset

    def access(self, addr: int):
        # Truncate to 32 bits (trace is 44-bit originally)
        addr32 = addr & 0xFFFFFFFF
        tag, idx, _ = self._split_address(addr32)
        hit = self.sets[idx].access(tag)

        self.hits += int(hit)
        self.misses += int(not hit)
        self.accesses += 1

    def summary(self, input_file: str) -> str:
        miss_rate = (self.misses / self.accesses) * 100 if self.accesses else 0.0
        assoc_desc = "fully-associative" if self.ways == self.num_lines else ("direct-mapped associativity" if self.ways == 1 else f"Number of ways = {self.ways}")
        lines = []
        lines.append("*" * 22)
        lines.append(f"file name: {input_file}")
        lines.append(f"Cache Size = {self.num_lines * self.block_size // 1024} KB")
        lines.append(f"Block Size = {self.block_size} B")
        if self.ways == 1:
            lines.append("direct-mapped associativity")
        elif self.ways == self.num_lines:
            lines.append("fully-associative mapping")
        else:
            lines.append(f"Number of ways = {self.ways}")
        lines.append(f"Number of Victim Cache = 0")
        lines.append(f"numOfOffsetBits = {self.offset_bits}")
        lines.append(f"numOfIndexBits = {self.index_bits}")
        lines.append(f"numOfTagBits = {self.tag_bits}")
        lines.append("")
        lines.append(f"Cache hit count= {self.hits}")
        lines.append(f"Cache miss count = {self.misses}")
        lines.append(f"Instruction count = {self.accesses}")
        lines.append(f"Cache miss rate = {miss_rate:.2f}%")
        lines.append("*" * 22)
        return "\n".join(lines)

def parse_trace_line(line: str) -> Tuple[str, int, int]:
    """
    Returns (op, offset_dec, address_int).
    Ignores blank/comment lines.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return ("", 0, -1)
    parts = line.split()
    if len(parts) < 3:
        # Some traces may omit offset; try to handle "L <addr>"
        if len(parts) == 2:
            op, addr_hex = parts
            offset = 0
        else:
            raise ValueError(f"Bad trace line: {line}")
    else:
        op, offset_str, addr_hex = parts[0], parts[1], parts[2]
        try:
            offset = int(offset_str, 10)
        except:
            offset = 0
    # Strip 0x if present
    addr_hex = addr_hex.lower().replace("0x", "")
    address = int(addr_hex, 16) + int(offset_str, 10)
    return (op.upper(), offset, address)

def run_sim(trace_path: str, cache_kb: int, block_size: int, ways: int):
    cache = Cache(cache_kb, block_size, ways)
    with open(trace_path, "r") as f:
        for line in f:
            op, _off, addr = parse_trace_line(line)
            if not op:
                continue
            # Treat both loads and stores as accesses
            cache.access(addr)
    print(cache.summary(trace_path))

def main():
    p = argparse.ArgumentParser(description="Simple Cache Simulator (LRU) per assignment spec")
    p.add_argument("-i", "--input", required=True, help="Trace file path (memtrace)")
    p.add_argument("-cs", "--cache-kb", required=True, type=int, help="Total cache size in KB (1 < cs < 4096)")
    p.add_argument("-bs", "--block-bytes", required=True, type=int, choices=[2,4,8,16,32,64], help="Cache block size in bytes")
    p.add_argument("-w", "--ways", required=True, type=int, help="Number of ways; use 0 for fully associative per assignment")
    args = p.parse_args()
    run_sim(args.input, args.cache_kb, args.block_bytes, args.ways)

if __name__ == "__main__":
    main()
