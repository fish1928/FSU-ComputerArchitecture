from typing import Self, Tuple


class ChainUnit():
    def __init__(self, id_unit):
        self.next = None
        self.previous = None
        self.id_unit = id_unit

        self._current = None
    # end

    def set_next(self, unit_next):
        self.next = unit_next
    # end

    def get_next(self) -> Self:
        return self.next
    # end

    def set_previous(self, unit_previous):
        self.previous = unit_previous
    # end
    
    def get_previous(self) -> Self:
        return self.previous
    # end

    def is_tail(self):
        return True if self.previous is None else False
    # end

    def is_head(self):
        return True if self.next is None else False
    # end

    def get_id(self) -> int:
        return self.id_unit
    # end

    def __next__(self) -> Self:
        if self._iter_current is None:
            raise StopIteration
        else:
            target = self._iter_current
            self._iter_current = self._iter_current.get_next()
            return target
        # end
    # end

    def __iter__(self):
        self._iter_current = self
        return self
    # end
# end


class ChainLine():  # factory

    INDEX_HEAD = -2
    INDEX_TAIL = -1

    @classmethod
    def generate_line(cls, num_units) -> Tuple[ChainUnit, ChainUnit, list]:
        tail = ChainUnit(-1)

        previous = tail
        for i in range(num_units):
            current = ChainUnit(i)
            previous.set_next(current)
            current.set_previous(previous)
            previous = current
        # end

        head = ChainUnit(-2)
        previous.set_next(head)
        head.set_previous(previous)

        index_line = [None]*(num_units+2)

        for unit in tail:
            index_line[unit.get_id()] = unit
        # end

        return head, tail, index_line
    # end
# end


class LRULine():
    def __init__(self, n_ways):
        head, tail, index_line = ChainLine.generate_line(n_ways)
        self.head = head
        self.tail = tail
        self.index_line = index_line
    # end

    def __len__(self):
        return len(self.index_line)
    # end

    def inspect(self):
        return [u.get_id() for u in self.tail]
    # end

    def get_head(self):
        return self.head
    # end

    def get_tail(self):
        return self.tail
    # end

    def _set_most(self, id_target):
        current = self.index_line[id_target]

        # take from original location
        current.get_previous().set_next(current.get_next())
        current.get_next().set_previous(current.get_previous())

        # set to target location(behind the most/head)
        head = self.head
        previous = head.get_previous()

        previous.set_next(current)
        current.set_previous(previous)

        current.set_next(head)
        head.set_previous(current)
    # end

    # def _set_least(self, id_target):
    #     current = self.index_line[id_target]

    #     # take from original location
    #     current.get_previous().set_next(current.get_next())
    #     current.get_next().set_previous(current.get_previous())

    #     # set to target location(behind the most/head)
    #     tail = self.tail
    #     next = tail.get_next()

    #     tail.set_next(current)
    #     current.set_previous(tail)

    #     current.set_next(next)
    #     next.set_previous(current)
    # # end

    def get_id_most(self):
        return self.head.get_previous().get_id()
    # end

    def get_id_least(self):
        return self.tail.get_next().get_id()
    # end

    def set_id_to_most(self, id_target):
        self._set_most(id_target)
    # end
# end

class LRULine_One(LRULine):
    def __init__(self, *args, **kvargs):
        head, tail, index_line = ChainLine.generate_line(1)
        self.head = head
        self.tail = tail
        self.target = self.tail.get_next()
        self.index_line = index_line
    # end

    def get_head(self):
        return self.head
    # end

    def get_tail(self):
        return self.tail
    # end

    def _set_most(self, id_target):
        pass
    # end

    def _set_least(self, id_target):
        pass
    # end

    def get_id_most(self):
        return self.target.get_id()
    # end

    def get_id_least(self):
        return self.target.get_id()
    # end

    def set_id_to_most(self, id_target):
        pass
    # end
# end



class NwayLRU():
    def __init__(self, n_lines, n_ways):

        # handle 0 way situation to make fully associate cache with l_lines way
        if n_ways == 0:
            n_ways = n_lines
            n_lines = 1
        # end

        # already handled outside, but do it again
        class_line_target = None
        match n_ways:
            case 1:
                class_line_target = LRULine_One # direct mapping
            case _:
                class_line_target = LRULine
            # end case
        # end match

        index_lines = [None] * n_lines
        for i in range(len(index_lines)):
            index_lines[i] = class_line_target(n_ways)
        # end

        self.index_lines = index_lines
    # end

    def touch(self, id_line, id_way):
        self.index_lines[id_line].set_id_to_most(id_way)
    # end

    def get_least(self, id_line):
        return self.index_lines[id_line].get_id_least()
    # end

    # def find_and_replace_v1(self, id_line) -> int:
    #    line_target = self.index_lines[id_line]
    #    id_least = line_target.get_id_least()
    #    line_target.set_id_to_most(id_least)
    #    return id_least
    # # end

    def shape(self):
        return (len(self.index_lines), len(self.index_lines[0])-2)
    # end

# end